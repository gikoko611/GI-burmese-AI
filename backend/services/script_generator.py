import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from backend.config import GROQ_API_KEY, COHERE_API_KEY
from backend.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptSegment,
)
from backend.services.analyzer import extract_video_id, fetch_transcript


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
COHERE_URL = "https://api.cohere.com/v2/chat"


def build_prompt(request: GenerateScriptRequest, transcript: str) -> str:
    return f"""
You are G.I Burmese AI, a professional Burmese YouTube script writer.

Create a natural, engaging Burmese narration script from the transcript below.

Content type: {request.contentType}
Script length: {request.scriptLength}
Narration style: {request.narrationStyle}
Output language: {request.outputLanguage}

Rules:
- Write primarily in natural Burmese Unicode.
- Do not translate word-for-word.
- Preserve important names, places, events, and facts.
- Do not invent information that is not supported by the transcript.
- Make it sound natural when spoken by a Burmese narrator.
- If the content is a movie/story recap, explain the story clearly and chronologically.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Return only the finished narration script.

TRANSCRIPT:
{transcript}
""".strip()


def call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert Burmese YouTube script writer.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }).encode("utf-8")

    request = Request(
        GROQ_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "G.I-Burmese-AI/1.0",
        },
        method="POST",
    )

    with urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


def call_cohere(prompt: str) -> str:
    if not COHERE_API_KEY:
        raise RuntimeError("COHERE_API_KEY is not configured.")

    payload = json.dumps({
        "model": "command-a-03-2025",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
    }).encode("utf-8")

    request = Request(
        COHERE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {COHERE_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "G.I-Burmese-AI/1.0",
        },
        method="POST",
    )

    with urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    content = data.get("message", {}).get("content", [])

    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        ]
        return "".join(text_parts).strip()

    return str(content).strip()


def generate_script(request: GenerateScriptRequest) -> GenerateScriptResponse:
    video_id = extract_video_id(request.url)

    transcript_data = fetch_transcript(video_id)
    transcript = transcript_data["transcript"]

    prompt = build_prompt(request, transcript)

    script = None
    provider = None
    errors = []

    # Primary: Groq
    try:
        script = call_groq(prompt)
        provider = "Groq"
    except Exception as exc:
        errors.append(f"Groq: {type(exc).__name__}: {exc}")

    # Fallback: Cohere
    if not script:
        try:
            script = call_cohere(prompt)
            provider = "Cohere"
        except Exception as exc:
            errors.append(f"Cohere: {type(exc).__name__}: {exc}")

    if not script:
        raise RuntimeError(
            "All AI providers failed. " + " | ".join(errors)
        )

    return GenerateScriptResponse(
        success=True,
        script=script,
        segments=[
            ScriptSegment(
                timestamp="00:00",
                heading="Burmese AI Narration",
                content=script,
            )
        ],
        wordCount=len(script.split()),
        characterCount=len(script),
        estimatedDuration=request.scriptLength,
        isDemoMode=False,
        disclaimer=(
            f"Real YouTube transcript processed successfully "
            f"using {provider}."
        ),
    )
