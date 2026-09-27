import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

from backend.schemas import VideoAnalysisResult


YOUTUBE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


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


def get_transcript(video_id: str) -> str:
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id)
    except Exception as exc:
        print(
            f"[Transcript Error] video_id={video_id} "
            f"type={type(exc).__name__} error={exc}",
            flush=True,
        )
        raise ValueError(
            f"Transcript unavailable: {type(exc).__name__}: {exc}"
        ) from exc

    text = " ".join(
        snippet.text.strip()
        for snippet in transcript
        if snippet.text.strip()
    )

    if not text:
        raise ValueError("The YouTube transcript is empty.")

    return text


def analyze_video(url: str) -> VideoAnalysisResult:
    video_id = extract_video_id(url)

    transcript = get_transcript(video_id)

    return VideoAnalysisResult(
        videoId=video_id,
        title="YouTube Video",
        duration=None,
        channel=None,
        detectedTopics=["YouTube", "Transcript", "Burmese AI"],
        suggestedContentType="General Explanation",
        isDemoMode=False,
        disclaimer=(
            f"Transcript loaded successfully. "
            f"{len(transcript)} characters available for AI analysis."
        ),
    )
