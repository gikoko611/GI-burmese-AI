import re
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
import json

from backend.schemas import VideoAnalysisResult


YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
TRANSCRIPT_API = "https://api.freetranscriptapi.com/v1/transcript"


def extract_video_id(url: str) -> str:
    value = url.strip()

    if not value:
        raise ValueError("YouTube URL is required.")

    parsed = urlparse(value)

    if parsed.netloc.lower() in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
    }:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/", 1)[1].split("/", 1)[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/", 1)[1].split("/", 1)[0]
        else:
            video_id = None

    elif parsed.netloc.lower() in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/", 1)[0]

    else:
        raise ValueError("Please provide a valid YouTube URL.")

    if not video_id or not YOUTUBE_ID_PATTERN.fullmatch(video_id):
        raise ValueError("Invalid YouTube video ID.")

    return video_id


def fetch_transcript(video_id: str) -> dict:
    query = urlencode({
        "video_url": f"https://www.youtube.com/watch?v={video_id}"
    })

    request = Request(
        f"{TRANSCRIPT_API}?{query}",
        headers={
            "User-Agent": "G.I-Burmese-AI/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError(
            f"Transcript provider request failed: {type(exc).__name__}: {exc}"
        ) from exc

    transcript_items = data.get("transcript", [])

    if not transcript_items:
        raise ValueError("Transcript provider returned no transcript.")

    transcript = " ".join(
        item.get("text", "").strip()
        for item in transcript_items
        if item.get("text", "").strip()
    )

    if not transcript:
        raise ValueError("Transcript is empty.")

    return {
        "title": data.get("title") or "YouTube Video",
        "language": data.get("language"),
        "transcript": transcript,
    }


def analyze_video(url: str) -> VideoAnalysisResult:
    video_id = extract_video_id(url)
    data = fetch_transcript(video_id)

    return VideoAnalysisResult(
        videoId=video_id,
        title=data["title"],
        duration=None,
        channel=None,
        detectedTopics=[
            "YouTube",
            "Transcript",
            "Burmese AI",
        ],
        suggestedContentType="General Explanation",
        isDemoMode=False,
        disclaimer=(
            f"Real transcript loaded successfully "
            f"({len(data['transcript'])} characters)."
        ),
    )
