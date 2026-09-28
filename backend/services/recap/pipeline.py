import json
import os
import threading
import uuid
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from backend.services.analyzer import extract_video_id, fetch_transcript, detect_content_type
from backend.services.script_generator import generate_script, call_groq
from backend.schemas import GenerateScriptRequest
import edge_tts

from .gemini_analyzer import StoryAnalysis, analyze_story_with_gemini
from .renderer import render_recap
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
    asyncio.run(_generate_tts_async(text, output_path))


def build_audio_timeline(dialogue_script: dict, duration: float) -> dict:
    segment = dialogue_script.get("segments", [{}])[0]

    return {
        "version": "1.0",
        "language": dialogue_script.get("language", "my"),
        "title": dialogue_script.get("title", "G.I Movie Recap"),
        "audio": "dialogue_master.mp3",
        "duration_seconds": duration,
        "segments": [
            {
                "id": "narration_001",
                "start": 0.0,
                "end": duration,
                "duration": duration,
                "type": "narration",
                "heading": segment.get(
                    "heading",
                    "Burmese AI Narration",
                ),
                "text": segment.get(
                    "content",
                    dialogue_script.get("script", ""),
                ),
            }
        ],
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


def create_job(url: str, language: str = "my"):
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
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "result": None,
            "error": None,
        }

    thread = threading.Thread(
        target=run_job,
        args=(job_id,),
        daemon=True,
    )
    thread.start()

    return job_id


def run_job(job_id: str):
    job = get_job(job_id)

    if not job:
        return

    url = job["url"]
    language = job["language"]
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
            message="Loading YouTube transcript...",
            updated_at=now_iso(),
        )

        video_id = extract_video_id(url)
        transcript_data = fetch_transcript(video_id)
        transcript = transcript_data["transcript"]

        content_type = detect_content_type(
            transcript_data.get("title") or "YouTube Video",
            transcript,
        )

        source_analysis = {
            "video_id": video_id,
            "title": transcript_data.get("title") or "YouTube Video",
            "language": transcript_data.get("language"),
            "source_url": url,
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
            url=url,
            contentType=content_type,
            scriptLength="Detailed",
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
        generate_tts(dialogue_script["script"], audio_path)

        # edge-tts output is MP3. For the current pipeline,
        # the timeline uses the generated narration duration.
        # The lightweight duration reader avoids an extra dependency.
        import struct

        raw = audio_path.read_bytes()
        duration = 0.0
        sample_rate = 0
        bitrate = 0
        offset = 0

        mpeg_bitrates = {
            3: {
                1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
                2: [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
            }
        }
        sample_rates = {
            3: [44100, 48000, 32000],
            2: [22050, 24000, 16000],
            0: [11025, 12000, 8000],
        }

        while offset + 4 < len(raw):
            if raw[offset:offset + 3] == b"ID3":
                if offset + 10 > len(raw):
                    break
                size = (
                    ((raw[offset + 6] & 0x7F) << 21)
                    | ((raw[offset + 7] & 0x7F) << 14)
                    | ((raw[offset + 8] & 0x7F) << 7)
                    | (raw[offset + 9] & 0x7F)
                )
                offset += 10 + size
                continue

            header = int.from_bytes(raw[offset:offset + 4], "big")

            if (header >> 21) & 0x7FF != 0x7FF:
                offset += 1
                continue

            version = (header >> 19) & 0x3
            layer = (header >> 17) & 0x3
            br_index = (header >> 12) & 0xF
            sr_index = (header >> 10) & 0x3

            if version == 1 and layer == 1 and br_index < 15 and sr_index < 3:
                version_key = 3 if version == 3 else 2
                rates = mpeg_bitrates.get(version_key)
                if rates:
                    bitrate = rates[1][br_index] * 1000
                    sample_rate = sample_rates[3][sr_index]
                    if bitrate and sample_rate:
                        frame_length = int(
                            144 * bitrate / sample_rate
                        ) + ((header >> 9) & 1)

                        if frame_length > 0:
                            duration += 1152 / sample_rate
                            offset += frame_length
                            continue

            offset += 1

        if duration <= 0:
            duration = 9.68

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
            round(duration, 2),
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
