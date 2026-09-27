import re
from urllib.parse import parse_qs, urlparse

from backend.schemas import VideoAnalysisResult


YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(url: str) -> str:
    value = url.strip()

    if not value:
        raise ValueError("YouTube URL is required.")

    parsed = urlparse(value)

    if parsed.netloc.lower() in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
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


def analyze_video(url: str) -> VideoAnalysisResult:
    video_id = extract_video_id(url)

    return VideoAnalysisResult(
        videoId=video_id,
        title="Demo YouTube Video",
        duration=None,
        channel=None,
        detectedTopics=["YouTube", "Content Analysis", "Burmese AI"],
        suggestedContentType="General Explanation",
        isDemoMode=True,
        disclaimer=(
            "Demo Mode: no real transcript or video media was downloaded. "
            "Connect an authorized transcript or metadata provider for real analysis."
        ),
    )
