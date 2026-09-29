import json
import os
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_UPLOAD_URL = (
    "https://generativelanguage.googleapis.com/upload/v1beta/files"
)


def extract_audio(video_path: Path, audio_path: Path) -> Path:
    """Extract mono audio from an uploaded video using FFmpeg."""

    if not video_path.exists():
        raise ValueError("Uploaded video file was not found.")

    audio_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "64k",
        str(audio_path),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("FFmpeg is not installed.") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Audio extraction timed out.") from exc

    if completed.returncode != 0:
        raise RuntimeError(
            "FFmpeg audio extraction failed: "
            + (completed.stderr[-2000:] or "unknown error")
        )

    if not audio_path.exists() or audio_path.stat().st_size == 0:
        raise RuntimeError("FFmpeg produced an empty audio file.")

    return audio_path


def _multipart_upload(
    file_path: Path,
    api_key: str,
    mime_type: str = "audio/mpeg",
) -> dict:
    """Upload a media file to Gemini Files API using REST."""

    if not file_path.exists():
        raise ValueError("Audio file does not exist.")

    file_size = file_path.stat().st_size
    display_name = file_path.name

    metadata = json.dumps(
        {
            "file": {
                "display_name": display_name,
            }
        }
    ).encode("utf-8")

    boundary = "----GI-Burmese-AI-Boundary"

    body = bytearray()

    body.extend(
        (
            f"--{boundary}\r\n"
            "Content-Disposition: form-data; "
            'name="metadata"\r\n'
            "Content-Type: application/json\r\n\r\n"
        ).encode()
    )
    body.extend(metadata)
    body.extend(b"\r\n")

    body.extend(
        (
            f"--{boundary}\r\n"
            "Content-Disposition: form-data; "
            f'name="file"; filename="{display_name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode()
    )

    body.extend(file_path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    request = Request(
        GEMINI_UPLOAD_URL,
        data=bytes(body),
        method="POST",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": f"multipart/related; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )

    try:
        with urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini file upload failed ({exc.code}): {detail[:1000]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Gemini file upload request failed: {exc}"
        ) from exc


def _generate_transcript(file_uri: str, mime_type: str, api_key: str) -> dict:
    """Ask Gemini to transcribe uploaded media."""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )

    prompt = """
Transcribe the uploaded audio accurately.

Return ONLY valid JSON with this schema:

{
  "title": "string",
  "language": "string",
  "transcript": "string",
  "segments": [
    {
      "start": 0.0,
      "end": 0.0,
      "text": "string"
    }
  ]
}

Rules:
- Preserve the actual spoken content.
- Do not invent missing speech.
- Keep the original spoken language in the transcript.
- Use seconds for timestamps.
- If exact word timestamps are unavailable, provide useful sentence/phrase timestamps.
- Return valid JSON only.
""".strip()

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "file_data": {
                            "mime_type": mime_type,
                            "file_uri": file_uri,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
        },
    }

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=600) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini transcription failed ({exc.code}): {detail[:1500]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Gemini transcription request failed: {exc}"
        ) from exc

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no transcription candidate.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(
        part.get("text", "")
        for part in parts
        if isinstance(part, dict)
    ).strip()

    if not text:
        raise RuntimeError("Gemini returned an empty transcription.")

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini transcription response was not valid JSON."
        ) from exc

    transcript = str(result.get("transcript", "")).strip()

    if not transcript:
        raise RuntimeError("Gemini returned no transcript text.")

    return {
        "title": result.get("title") or "Uploaded Video",
        "language": result.get("language"),
        "transcript": transcript,
        "segments": result.get("segments", []),
        "provider": "Gemini",
    }


def transcribe_uploaded_video(video_path: Path, job_dir: Path) -> dict:
    """Extract audio and transcribe an uploaded video with Gemini."""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    audio_path = job_dir / "audio_for_transcription.mp3"

    extract_audio(video_path, audio_path)

    uploaded = _multipart_upload(
        audio_path,
        GEMINI_API_KEY,
        "audio/mpeg",
    )

    file_info = uploaded.get("file", uploaded)

    file_uri = file_info.get("uri")
    mime_type = file_info.get("mimeType", "audio/mpeg")

    if not file_uri:
        raise RuntimeError(
            "Gemini file upload returned no file URI."
        )

    result = _generate_transcript(
        file_uri=file_uri,
        mime_type=mime_type,
        api_key=GEMINI_API_KEY,
    )

    result["audio_path"] = str(audio_path.name)
    result["gemini_file_uri"] = file_uri

    return result
