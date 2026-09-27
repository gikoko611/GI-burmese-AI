import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from backend.services.analyzer import extract_video_id, fetch_transcript
from backend.services.script_generator import generate_script
from backend.schemas import GenerateScriptRequest


DEFAULT_RECAP_DIR = Path(__file__).resolve().parents[3] / "runtime" / "recaps"

BASE_DIR = Path(
    os.getenv("RECAP_OUTPUT_DIR", str(DEFAULT_RECAP_DIR))
)

BASE_DIR.mkdir(parents=True, exist_ok=True)

_jobs = {}
_jobs_lock = threading.Lock()


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

        source_analysis = {
            "video_id": video_id,
            "title": transcript_data.get("title") or "YouTube Video",
            "language": transcript_data.get("language"),
            "source_url": url,
            "transcript_character_count": len(transcript),
            "analysis_type": "transcript_based",
            "created_at": now_iso(),
        }

        write_json(
            job_dir / "source_analysis.json",
            source_analysis,
        )

        # ---------------------------------------------------------
        # STEP 2 — Character extraction placeholder
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Building story structure",
            progress=30,
            message="Preparing characters and story structure...",
            updated_at=now_iso(),
        )

        characters = {
            "status": "pending_ai_character_extraction",
            "characters": [],
            "note": (
                "Character extraction will be upgraded to Gemini "
                "multimodal analysis in the next pipeline stage."
            ),
        }

        write_json(
            job_dir / "characters.json",
            characters,
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
            contentType="Movie Recap",
            scriptLength="Detailed",
            narrationStyle="Storytelling",
            outputLanguage="Burmese",
        )

        script_result = generate_script(script_request)

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
        # STEP 4 — Finish foundation
        # ---------------------------------------------------------
        update_job(
            job_id,
            step="Finalizing",
            progress=90,
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
                "dialogue_script.json",
            ],
            "audio_status": "not_started",
            "video_status": "not_started",
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
            "dialogue_script": "dialogue_script.json",
            "report": "report.json",
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
