import json
import os
import threading
import uuid
import asyncio
import subprocess
import shutil
from datetime import datetime, timezone
from pathlib import Path

from backend.services.analyzer import extract_video_id, fetch_transcript, detect_content_type
from backend.services.script_generator import generate_script, call_groq
from backend.schemas import GenerateScriptRequest
import edge_tts

from .gemini_analyzer import StoryAnalysis, analyze_story_with_gemini
from .renderer import render_recap
from .local_transcriber import transcribe_uploaded_video
DEFAULT_RECAP_DIR = Path(__file__).resolve().parents[3] / "runtime" / "recaps"

BASE_DIR = Path(
    os.getenv("RECAP_OUTPUT_DIR", str(DEFAULT_RECAP_DIR))
)

BASE_DIR.mkdir(parents=True, exist_ok=True)

_jobs = {}
_jobs_lock = threading.Lock()



def analyze_story_with_groq(transcript: str, title: str = "YouTube Video"):
    prompt = f"""
You are a professional movie/story recap analyst.

Analyze the following transcript and return ONLY valid JSON.
Do not use Markdown fences.

Required JSON schema:
{{
  "title": "string",
  "genre": "string",
  "premise": "string",
  "characters": [
    {{
      "id": "string",
      "name": "string",
      "role": "protagonist|antagonist|supporting|other",
      "description": "string",
      "voice_profile": "male|female|neutral"
    }}
  ],
  "scenes": [
    {{
      "id": "string",
      "order": 1,
      "title": "string",
      "summary": "string",
      "characters": ["character_id"],
      "important": true
    }}
  ],
  "events": [
    {{
      "order": 1,
      "scene_id": "scene_1",
      "event": "string",
      "consequence": "string"
    }}
  ],
  "conflict": "string",
  "ending": "string",
  "recap_focus": ["string"]
}}

Rules:
- Follow the actual transcript.
- Identify important characters and their roles.
- Break the story into chronological scenes.
- Extract important events and consequences.
- Do not invent events that are not supported by the transcript.
- This will be used to create a Burmese movie recap.
- Return JSON only.

Title:
{title}

Transcript:
{transcript}
"""

    raw = call_groq(prompt).strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "", 1)
        raw = raw.replace("```", "", 1).strip()

    analysis = StoryAnalysis.parse_raw(raw)
    return analysis.dict()

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def update_job(job_id, **updates):
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)


def get_job(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        return dict(job)


def write_json(path: Path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def _generate_tts_async(text: str, output_path: Path):
    communicate = edge_tts.Communicate(
        text,
        "my-MM-NilarNeural",
        rate="+0%",
        volume="+0%",
        pitch="+0Hz",
    )
    await communicate.save(str(output_path))


def generate_tts(text: str, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_generate_tts_async(text, output_path))


def build_audio_timeline(
    dialogue_script: dict,
    duration: float,
    segment_durations: list[float] | None = None,
) -> dict:
    raw_segments = dialogue_script.get("segments") or []

    if not raw_segments:
        raw_segments = [
            {
                "timestamp": "",
                "heading": "Burmese AI Narration",
                "content": dialogue_script.get("script", ""),
            }
        ]

    # When per-segment TTS durations are available, use them directly.
    # Otherwise distribute the total narration duration proportionally
    # to each segment's text length.
    if segment_durations and len(segment_durations) == len(raw_segments):
        durations = [max(float(value), 0.01) for value in segment_durations]
    else:
        weights = [
            max(len(str(segment.get("content", "")).strip()), 1)
            for segment in raw_segments
        ]
        total_weight = sum(weights) or 1
        durations = [
            duration * weight / total_weight
            for weight in weights
        ]

    scale = duration / sum(durations) if sum(durations) > 0 else 1.0
    durations = [value * scale for value in durations]

    timeline_segments = []
    current = 0.0

    for index, (segment, segment_duration) in enumerate(
        zip(raw_segments, durations),
        start=1,
    ):
        start = current
        end = (
            duration
            if index == len(raw_segments)
            else min(duration, current + segment_duration)
        )

        timeline_segments.append(
            {
                "id": f"narration_{index:03d}",
                "start": round(start, 3),
                "end": round(end, 3),
                "duration": round(end - start, 3),
                "type": "narration",
                "heading": segment.get(
                    "heading",
                    "Burmese AI Narration",
                ),
                "text": segment.get(
                    "content",
                    "",
                ),
                "timestamp": segment.get("timestamp", ""),
            }
        )

        current = end

    return {
        "version": "1.0",
        "language": dialogue_script.get("language", "my"),
        "title": dialogue_script.get("title", "G.I Movie Recap"),
        "audio": "dialogue_master.mp3",
        "duration_seconds": round(duration, 3),
        "segments": timeline_segments,
        "created_at": now_iso(),
    }


def build_edit_plan(timeline: dict) -> dict:
    duration = float(timeline["duration_seconds"])

    return {
        "version": "1.0",
        "title": timeline["title"],
        "duration_seconds": duration,
        "audio": "dialogue_master.mp3",
        "media_policy": "authorized_media_only",
        "render_status": "pending_media",
        "segments": [
            {
                "id": segment["id"],
                "start": segment["start"],
                "end": segment["end"],
                "visual": {
                    "source": "authorized_media",
                    "source_start": segment["start"],
                    "source_end": segment["end"],
                    "fallback": "generated_background",
                },
                "audio": {
                    "file": "dialogue_master.mp3",
                    "start": segment["start"],
                    "end": segment["end"],
                },
                "caption": {
                    "enabled": True,
                    "text": segment["text"],
                    "language": timeline["language"],
                },
            }
            for segment in timeline["segments"]
        ],
        "created_at": now_iso(),
    }


def create_job(
    url: str | None = None,
    language: str = "my",
    source_type: str = "youtube",
    script_length: str = "Detailed",
    auto_start: bool = True,
):
    job_id = f"recap_{uuid.uuid4().hex[:12]}"

    job_dir = BASE_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    with _jobs_lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "step": "Queued",
            "progress": 0,
            "message": "Recap job created.",
            "url": url,
            "language": language,
            "source_type": source_type,
            "script_length": script_length,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "result": None,
            "error": None,
            "started": False,
        }

    if auto_start:
        start_job(job_id)

    return job_id


def start_job(job_id: str) -> bool:
    with _jobs_lock:
        job = _jobs.get(job_id)

        if not job:
            return False

        if job.get("started"):
            return False

        job["started"] = True
        job["updated_at"] = now_iso()

    thread = threading.Thread(
        target=run_job,
        args=(job_id,),
        daemon=True,
    )
    thread.start()

    return True


def run_job(job_id: str):
    job = get_job(job_id)

    if not job:
        return

    url = job["url"]
    language = job["language"]
    source_type = job.get("source_type", "youtube").strip().lower()
    script_length = job.get("script_length", "Detailed")
    job_dir = BASE_DIR / job_id

    try:
        # ---------------------------------------------------------
        # STEP 1 — Analyze source
        # ---------------------------------------------------------
        update_job(
            job_id,
            status="running",
            step="Analyzing video",
            progress=15,
            message=(
                "Loading YouTube transcript..."
                if source_type == "youtube"
                else "Preparing uploaded video..."
            ),
            updated_at=now_iso(),
        )

        if source_type == "youtube":
            if not url:
                raise ValueError("YouTube source requires a URL.")

            video_id = extract_video_id(url)
            transcript_data = fetch_transcript(video_id)
            transcript = transcript_data["transcript"]

            source_title = transcript_data.get("title") or "YouTube Video"
            source_language = transcript_data.get("language")
            source_url = url

        elif source_type == "upload":
            media_candidates = sorted(job_dir.glob("authorized_media.*"))

            if not media_candidates:
                raise ValueError(
                    "Uploaded video is required before starting an upload job."
                )

            media_path = media_candidates[0]

            update_job(
                job_id,
                step="Transcribing uploaded video",
                progress=22,
                message="Extracting audio and transcribing with Gemini...",
                updated_at=now_iso(),
            )

            transcript_data = transcribe_uploaded_video(
                video_path=media_path,
                job_dir=job_dir,
            )

            transcript = transcript_data["transcript"]
            source_title = transcript_data.get("title") or "Uploaded Video"
            source_language = transcript_data.get("language")
            source_url = None

            write_json(
                job_dir / "uploaded_transcript.json",
                transcript_data,
            )

        else:
            raise ValueError(
                f"Unsupported source_type: {source_type}"
            )

        content_type = detect_content_type(
            source_title,
            transcript,
        )

        source_analysis = {
            "source_type": source_type,
            "video_id": video_id if source_type == "youtube" else None,
            "title": source_title,
            "language": source_language,
            "source_url": source_url,
            "transcript_character_count": len(transcript),
            "analysis_type": "transcript_based",
            "content_type": content_type,
            "created_at": now_iso(),
        }

        write_json(
            job_dir / "source_analysis.json",
            source_analysis,
        )

        # ---------------------------------------------------------
        # STEP 2 — Story intelligence (Movie/Drama only)
        # ---------------------------------------------------------
        story_analysis = None
        story_provider = None

        if content_type == "Movie Recap":
            update_job(
                job_id,
                step="Analyzing story with Gemini",
                progress=30,
                message="Extracting characters, scenes and story events...",
                updated_at=now_iso(),
            )

            try:
                story_analysis = analyze_story_with_gemini(
                    transcript=transcript,
                    title=transcript_data.get("title") or "YouTube Video",
                )
                story_provider = "gemini"
            except Exception as exc:
                print(
                    f"[recap] Gemini story analysis failed: "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )
                print(
                    "[recap] Falling back to Groq story analysis.",
                    flush=True,
                )

                story_analysis = analyze_story_with_groq(
                    transcript=transcript,
                    title=transcript_data.get("title") or "YouTube Video",
                )
                story_provider = "groq"

            write_json(
                job_dir / "source_analysis.json",
                {
                    **source_analysis,
                    "analysis_type": "structured_story_analysis",
                    "story_provider": story_provider,
                    "story": story_analysis,
                },
            )

            characters = {
                "status": "complete",
                "characters": story_analysis.get("characters", []),
                "voice_profiles": {
                    character["id"]: character.get(
                        "voice_profile",
                        "neutral",
                    )
                    for character in story_analysis.get(
                        "characters",
                        [],
                    )
                },
                "created_at": now_iso(),
            }

            write_json(
                job_dir / "characters.json",
                characters,
            )

            write_json(
                job_dir / "story_analysis.json",
                story_analysis,
            )
        else:
            # Music and general content must not be forced through
            # the movie/story analyzer.
            write_json(
                job_dir / "source_analysis.json",
                {
                    **source_analysis,
                    "analysis_type": "transcript_based",
                    "content_type": content_type,
                    "story_provider": None,
                    "story": None,
                },
            )

            write_json(
                job_dir / "characters.json",
                {
                    "status": "not_applicable",
                    "characters": [],
                    "voice_profiles": {},
                    "created_at": now_iso(),
                },
            )

            write_json(
                job_dir / "story_analysis.json",
                {
                    "status": "not_applicable",
                    "content_type": content_type,
                    "characters": [],
                    "scenes": [],
                    "events": [],
                },
            )

        # ---------------------------------------------------------
        # STEP 3 — Burmese recap script
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Writing Burmese recap",
            progress=55,
            message="Generating natural Burmese narration...",
            updated_at=now_iso(),
        )

        script_request = GenerateScriptRequest(
            url=url or "",
            contentType=content_type,
            scriptLength=script_length,
            narrationStyle="Storytelling",
            outputLanguage="Burmese",
        )

        script_result = generate_script(script_request, story_context=story_analysis)

        dialogue_script = {
            "language": language,
            "title": transcript_data.get("title") or "G.I Movie Recap",
            "source_url": url,
            "script": script_result.script,
            "segments": [
                {
                    "timestamp": segment.timestamp,
                    "heading": segment.heading,
                    "content": segment.content,
                }
                for segment in script_result.segments
            ],
            "word_count": script_result.wordCount,
            "character_count": script_result.characterCount,
            "estimated_duration": script_result.estimatedDuration,
            "provider_disclaimer": script_result.disclaimer,
            "created_at": now_iso(),
        }

        write_json(
            job_dir / "dialogue_script.json",
            dialogue_script,
        )

        # ---------------------------------------------------------
        # STEP 4 — Burmese TTS
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Generating Burmese audio",
            progress=65,
            message="Creating Burmese narration audio...",
            updated_at=now_iso(),
        )

        audio_path = job_dir / "dialogue_master.mp3"

        # Generate Burmese TTS one segment at a time so the real audio
        # duration of every narration segment can drive caption timing.
        raw_segments = dialogue_script.get("segments") or []

        if not raw_segments:
            raw_segments = [
                {
                    "timestamp": "",
                    "heading": "Burmese AI Narration",
                    "content": dialogue_script.get("script", ""),
                }
            ]

        segment_audio_dir = job_dir / "segments_audio"
        segment_audio_dir.mkdir(parents=True, exist_ok=True)

        segment_durations = []
        segment_audio_files = []

        for index, segment in enumerate(raw_segments, start=1):
            text = str(segment.get("content", "")).strip()

            if not text:
                continue

            segment_audio_path = (
                segment_audio_dir / f"segment_{index:03d}.mp3"
            )

            update_job(
                job_id,
                step="Generating Burmese audio",
                progress=min(65 + int((index - 1) * 8 / max(len(raw_segments), 1)), 72),
                message=f"Creating Burmese narration segment {index}/{len(raw_segments)}...",
                updated_at=now_iso(),
            )

            generate_tts(text, segment_audio_path)

            if not segment_audio_path.exists():
                raise RuntimeError(
                    f"TTS segment was not created: {segment_audio_path.name}"
                )

            if not shutil.which("ffprobe"):
                raise RuntimeError(
                    "ffprobe is required to measure TTS segment duration."
                )

            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(segment_audio_path),
                ],
                capture_output=True,
                text=True,
            )

            if probe.returncode != 0:
                detail = probe.stderr.strip() or "Unknown ffprobe error."
                raise RuntimeError(
                    f"Could not measure TTS segment duration: {detail}"
                )

            try:
                segment_duration = float(probe.stdout.strip())
            except ValueError as exc:
                raise RuntimeError(
                    f"Invalid TTS duration for {segment_audio_path.name}: "
                    f"{probe.stdout.strip()!r}"
                ) from exc

            if segment_duration <= 0:
                raise RuntimeError(
                    f"Invalid TTS segment duration: {segment_audio_path.name}"
                )

            segment_durations.append(segment_duration)
            segment_audio_files.append(segment_audio_path)

        if not segment_audio_files:
            raise RuntimeError("No narration segments were generated.")

        # Concatenate all segment MP3 files into the master narration.
        concat_list = segment_audio_dir / "concat.txt"

        def _concat_path(path: Path) -> str:
            value = str(path.resolve())
            return value.replace("\\", "\\\\").replace("'", "\\'")

        concat_list.write_text(
            "".join(
                f"file '{_concat_path(path)}'\n"
                for path in segment_audio_files
            ),
            encoding="utf-8",
        )

        update_job(
            job_id,
            step="Combining Burmese audio",
            progress=73,
            message="Combining synchronized narration segments...",
            updated_at=now_iso(),
        )

        if not shutil.which("ffmpeg"):
            raise RuntimeError("FFmpeg is required to combine narration segments.")

        concat_result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c:a",
                "libmp3lame",
                "-b:a",
                "128k",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
        )

        if concat_result.returncode != 0:
            error_lines = concat_result.stderr.strip().splitlines()
            detail = error_lines[-1] if error_lines else "Unknown FFmpeg error."
            raise RuntimeError(
                f"Failed to combine narration segments: {detail}"
            )

        duration = sum(segment_durations)

        # ---------------------------------------------------------
        # STEP 5 — Audio timeline
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Building audio timeline",
            progress=75,
            message="Synchronizing narration timeline...",
            updated_at=now_iso(),
        )

        timeline = build_audio_timeline(
            dialogue_script,
            round(duration, 3),
            segment_durations=segment_durations,
        )

        write_json(
            job_dir / "audio_timeline.json",
            timeline,
        )

        # ---------------------------------------------------------
        # STEP 6 — Edit plan
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Building edit plan",
            progress=85,
            message="Preparing video edit plan...",
            updated_at=now_iso(),
        )

        edit_plan = build_edit_plan(timeline)

        write_json(
            job_dir / "edit_plan.json",
            edit_plan,
        )

        # ---------------------------------------------------------
        # STEP 7 — Finish foundation
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Finalizing",
            progress=95,
            message="Saving recap artifacts...",
            updated_at=now_iso(),
        )

        report = {
            "job_id": job_id,
            "status": "complete",
            "source": source_analysis,
            "artifacts": [
                "source_analysis.json",
                "characters.json",
                "story_analysis.json",
                "dialogue_script.json",
                "dialogue_master.mp3",
                "audio_timeline.json",
                "edit_plan.json",
            ],
            "audio_status": "complete",
            "video_status": "pending_authorized_media",
            "audio_duration_seconds": round(duration, 2),
            "created_at": now_iso(),
        }

        write_json(
            job_dir / "report.json",
            report,
        )

        result = {
            "job_directory": str(job_dir),
            "source_analysis": "source_analysis.json",
            "characters": "characters.json",
            "story_analysis": "story_analysis.json",
            "dialogue_script": "dialogue_script.json",
            "report": "report.json",
            "audio": "dialogue_master.mp3",
            "audio_timeline": "audio_timeline.json",
            "edit_plan": "edit_plan.json",
            "video_status": "pending_authorized_media",
            "script": script_result.script,
            "word_count": script_result.wordCount,
            "character_count": script_result.characterCount,
            "estimated_duration": script_result.estimatedDuration,
        }

        update_job(
            job_id,
            status="complete",
            step="Complete",
            progress=100,
            message="Burmese recap generated successfully.",
            result=result,
            updated_at=now_iso(),
        )

    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

        print(
            f"[recap:{job_id}] FAILED: {error}",
            flush=True,
        )

        update_job(
            job_id,
            status="failed",
            step="Failed",
            progress=0,
            message="Recap generation failed.",
            error=error,
            updated_at=now_iso(),
        )
