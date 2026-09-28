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
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10) "
                "AppleWebKit/537.36 "
                "Chrome/140 Mobile Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Connection": "close",
        },
    )

    last_error = None

    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                break
        except Exception as exc:
            last_error = exc

            if attempt < 2:
                print(
                    f"[transcript] request failed "
                    f"({type(exc).__name__}: {exc}); "
                    f"retry {attempt + 2}/3...",
                    flush=True,
                )
                continue

            raise ValueError(
                "Transcript provider request failed: "
                f"{type(exc).__name__}: {exc}"
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


def detect_content_type(title: str, transcript: str) -> str:
    """
    Detect the most appropriate G.I Burmese AI content type.

    Music is intentionally not supported. Unknown content falls back
    to General Explanation.
    """
    title_text = (title or "").lower().strip()
    transcript_text = (transcript or "").lower().strip()
    combined = f"{title_text}\n{transcript_text}"

    # Movie / drama / story content
    movie_markers = (
        "movie",
        "full movie",
        "short film",
        "film",
        "episode",
        "drama",
        "trailer",
        "movie recap",
        "story",
    )

    # Tips / tricks / how-to content
    tips_markers = (
        "tips",
        "tricks",
        "tips and tricks",
        "how to",
        "tutorial",
        "guide",
        "ways to",
        "best way",
        "step by step",
        "steps to",
    )

    # Technology / coding content
    tech_markers = (
        "python",
        "javascript",
        "typescript",
        "coding",
        "programming",
        "software",
        "linux",
        "android",
        "github",
        "api",
        "database",
        "developer",
        "technology",
        "tech",
    )

    # Educational content
    education_markers = (
        "learn",
        "lesson",
        "education",
        "educational",
        "course",
        "explained",
        "science",
        "history",
        "mathematics",
        "physics",
        "biology",
    )

    # News / current-events content
    news_markers = (
        "news",
        "breaking news",
        "latest news",
        "update",
        "current events",
        "report",
    )

    # Informational explanation
    explanation_markers = (
        "explained",
        "explanation",
        "what is",
        "why",
        "how does",
        "meaning",
        "facts about",
    )

    if any(marker in title_text for marker in movie_markers):
        return "Movie Recap"

    if any(marker in title_text for marker in tech_markers):
        return "Tech"

    if any(marker in title_text for marker in news_markers):
        return "News"

    if any(marker in title_text for marker in explanation_markers):
        return "Explanation"

    if any(marker in title_text for marker in tips_markers):
        return "Tips & Tricks"

    if any(marker in title_text for marker in education_markers):
        return "Educational"

    # Use transcript signals only when the title is not enough.
    if any(marker in transcript_text for marker in tech_markers):
        return "Tech"

    if any(marker in transcript_text for marker in news_markers):
        return "News"

    if any(marker in transcript_text for marker in explanation_markers):
        return "Explanation"

    if any(marker in transcript_text for marker in tips_markers):
        return "Tips & Tricks"

    if any(marker in transcript_text for marker in education_markers):
        return "Educational"

    # Story-like content
    story_markers = (
        "once upon a time",
        "story begins",
        "the story begins",
        "narrator",
        "character",
        "chapter",
    )

    if any(marker in combined for marker in story_markers):
        return "Story"

    return "General Explanation"


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
        suggestedContentType=detect_content_type(
            data["title"],
            data["transcript"],
        ),
        isDemoMode=False,
        disclaimer=(
            f"Real transcript loaded successfully "
            f"({len(data['transcript'])} characters)."
        ),
    )
