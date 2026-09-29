from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"
MYANMAR_FONT = FONT_DIR / "NotoSansMyanmar-Regular.otf"


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


def _ass_time(seconds: float) -> str:
    total_cs = max(0, round(float(seconds) * 100))

    hours, remainder = divmod(total_cs, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, centisecs = divmod(remainder, 100)

    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"


def _ass_text(value: str) -> str:
    text = str(value or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\\", r"\\")
    text = text.replace("{", r"\{")
    text = text.replace("}", r"\}")
    text = text.replace("\n", r"\N")
    return text


def _write_ass_captions(
    timeline: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1280",
        "PlayResY: 720",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, "
            "SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
            "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
            "MarginV, Encoding"
        ),
        (
            "Style: Burmese,Noto Sans Myanmar,42,"
            "&H00FFFFFF,&H000000FF,&H00000000,&H90000000,"
            "0,0,0,0,100,100,0,0,1,2,1,2,50,50,40,1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "MarginV, Effect, Text",
    ]

    for segment in timeline.get("segments", []):
        start = float(segment.get("start", 0))
        end = float(segment.get("end", start))
        text = _ass_text(segment.get("text", ""))

        if not text or end <= start:
            continue

        lines.append(
            "Dialogue: 0,"
            f"{_ass_time(start)},"
            f"{_ass_time(end)},"
            "Burmese,,0,0,0,,"
            f"{text}"
        )

    output_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _escape_filter_path(path: Path) -> str:
    value = str(path.resolve())
    value = value.replace("\\", r"\\")
    value = value.replace(":", r"\:")
    value = value.replace("'", r"\'")
    return value


def render_recap(
    job_dir: str | Path,
    media_path: str | Path | None = None,
) -> dict:
    job = Path(job_dir)

    timeline_path = job / "audio_timeline.json"
    plan_path = job / "edit_plan.json"
    audio_path = job / "dialogue_master.mp3"
    captions_path = job / "dialogue_captions.ass"
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

    if media_path is None:
        return {
            "status": "pending_media",
            "output": None,
            "duration_seconds": duration,
            "reason": (
                "Authorized source media is required for final rendering."
            ),
        }

    media = Path(media_path)

    if not media.exists():
        raise FileNotFoundError(
            f"Authorized media not found: {media}"
        )

    if not FONT_DIR.exists():
        raise FileNotFoundError(
            f"Burmese font directory not found: {FONT_DIR}"
        )

    if not MYANMAR_FONT.exists():
        raise FileNotFoundError(
            f"Burmese font not found: {MYANMAR_FONT}"
        )

    # ---------------------------------------------------------
    # Generate ASS captions from the real audio timeline.
    # ---------------------------------------------------------
    _write_ass_captions(
        timeline,
        captions_path,
    )

    if not captions_path.exists():
        raise RuntimeError(
            "dialogue_captions.ass was not created."
        )

    # ---------------------------------------------------------
    # Final render:
    # authorized video
    # + Burmese narration
    # + burned Burmese captions
    # ---------------------------------------------------------
    subtitle_file = _escape_filter_path(captions_path)
    font_dir = _escape_filter_path(FONT_DIR)

    subtitle_filter = (
        f"subtitles='{subtitle_file}':"
        f"fontsdir='{font_dir}'"
    )

    _run_ffmpeg([
        "-stream_loop", "-1",
        "-i", str(media),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", subtitle_filter,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_path),
    ])

    if not output_path.exists():
        raise RuntimeError(
            "FFmpeg completed but final_recap.mp4 was not created."
        )

    return {
        "status": "complete",
        "output": str(output_path),
        "duration_seconds": duration,
        "segments": len(plan.get("segments", [])),
        "captions": str(captions_path),
        "font": str(MYANMAR_FONT),
    }
