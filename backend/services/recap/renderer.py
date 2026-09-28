from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _run_ffmpeg(args: list[str]) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed on this server.")

    result = subprocess.run(
        ["ffmpeg", "-y", *args],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        error = result.stderr.strip().splitlines()
        detail = error[-1] if error else "Unknown FFmpeg error."
        raise RuntimeError(f"FFmpeg render failed: {detail}")


def render_recap(
    job_dir: str | Path,
    media_path: str | Path | None = None,
) -> dict:
    job = Path(job_dir)

    timeline_path = job / "audio_timeline.json"
    plan_path = job / "edit_plan.json"
    audio_path = job / "dialogue_master.mp3"
    output_path = job / "final_recap.mp4"

    if not timeline_path.exists():
        raise FileNotFoundError("audio_timeline.json not found.")

    if not plan_path.exists():
        raise FileNotFoundError("edit_plan.json not found.")

    if not audio_path.exists():
        raise FileNotFoundError("dialogue_master.mp3 not found.")

    timeline = json.loads(
        timeline_path.read_text(encoding="utf-8")
    )
    plan = json.loads(
        plan_path.read_text(encoding="utf-8")
    )

    duration = float(timeline.get("duration_seconds", 0))

    if duration <= 0:
        raise ValueError("Invalid audio duration.")

    # Rendering requires media supplied by the user/server.
    # No automatic movie downloading is performed.
    if media_path is None:
        return {
            "status": "pending_media",
            "output": None,
            "duration_seconds": duration,
            "reason": "Authorized source media is required for final rendering.",
        }

    media = Path(media_path)

    if not media.exists():
        raise FileNotFoundError(
            f"Authorized media not found: {media}"
        )

    # Basic single-source render:
    # authorized video + Burmese narration audio.
    _run_ffmpeg([
        "-stream_loop", "-1",
        "-i", str(media),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ])

    return {
        "status": "complete",
        "output": str(output_path),
        "duration_seconds": duration,
        "segments": len(plan.get("segments", [])),
    }
