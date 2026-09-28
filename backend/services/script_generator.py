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


def build_prompt(
    request: GenerateScriptRequest,
    transcript: str,
    story_context: dict | None = None,
) -> str:
    story_context_text = ""

    if story_context:
        story_context_text = json.dumps(
            {
                "title": story_context.get("title", ""),
                "genre": story_context.get("genre", ""),
                "premise": story_context.get("premise", ""),
                "characters": story_context.get("characters", []),
                "scenes": story_context.get("scenes", []),
                "events": story_context.get("events", []),
                "conflict": story_context.get("conflict", ""),
                "ending": story_context.get("ending", ""),
                "recap_focus": story_context.get("recap_focus", []),
            },
            ensure_ascii=False,
            indent=2,
        )

    return f"""
You are G.I Burmese AI, a professional Burmese movie/story recap writer.

Create a natural, engaging Burmese narration script.

Content type: {request.contentType}
Script length: {request.scriptLength}
Narration style: {request.narrationStyle}
Output language: {request.outputLanguage}

STORY INTELLIGENCE:
{story_context_text}

When Story Intelligence is provided:
- Use it as the primary story structure.
- Follow the scenes in chronological order.
- Introduce important characters naturally.
- Explain important events and their consequences.
- Build the narration around the central conflict.
- Lead naturally toward the ending.
- Use character names and roles from the story analysis.
- Do not invent events that contradict the story analysis.
- Do not simply explain what the video is.
- Write an actual story/movie recap.

Rules:
- Write in fluent, natural Myanmar Burmese (မြန်မာစာ) suitable for spoken narration.
- Do NOT translate sentence-by-sentence or word-for-word.
- Use normal conversational Burmese grammar and natural Myanmar vocabulary.
- Avoid awkward literal translations and unnatural phrases.
- Preserve important names, places, events, and facts.
- Do not invent unsupported facts.
- Focus on important characters, events, conflict, consequences, and outcome.
- Write as an experienced Burmese YouTube narrator explaining the story to viewers.
- Do not reproduce long passages of the original transcript or song lyrics.
- For songs, summarize meaning and theme instead of reproducing lyrics.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Return only the finished narration script.
- Do not start with meta text such as "ဒီစာတမ်းကို..." or "မြန်မာဘာသာဖြင့်..."
- Do not repeat the same sentence or idea multiple times.
- Avoid generic filler and artificial phrases.
- Prefer concise, human-sounding Burmese narration.
- Do not create artificial "အစပိုင်း / အလယ်ပိုင်း / နောက်ဆုံးပိုင်း" headings.

TRANSCRIPT:
{transcript}
""".strip()

def call_gemini(prompt: str) -> str:
    """Generate Burmese narration using Gemini REST API."""
    import json
    import os
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096,
        },
    }

    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "G.I-Burmese-AI/1.0",
        },
        method="POST",
    )

    import time

    last_error = None

    for attempt, delay in enumerate((0, 3, 7), start=1):
        try:
            with urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            break

        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(
                f"Gemini HTTP {exc.code}: {body[:500]}"
            )

            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise last_error from exc

            print(
                f"[generate-script] Gemini HTTP {exc.code}; "
                f"retry {attempt + 1}/3 after {delay or 3}s...",
                flush=True,
            )
            time.sleep(delay or 3)

        except URLError as exc:
            last_error = RuntimeError(
                f"Gemini network error: {exc}"
            )

            if attempt == 3:
                raise last_error from exc

            print(
                f"[generate-script] Gemini network error; "
                f"retry {attempt + 1}/3 after {delay or 3}s...",
                flush=True,
            )
            time.sleep(delay or 3)
    else:
        raise last_error or RuntimeError("Gemini request failed.")

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates: "
            + json.dumps(data)[:500]
        )

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(
        part.get("text", "")
        for part in parts
        if part.get("text")
    ).strip()

    if not text:
        raise RuntimeError("Gemini returned an empty script.")

    return text


def call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload = json.dumps({
        "model": "openai/gpt-oss-120b",
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


def clean_script(text: str) -> str:
    """Remove common AI boilerplate and obvious repeated paragraphs."""
    text = text.strip()

    unwanted_starts = (
        "ဒီစာတမ်းကို",
        "ဒီစာကို",
        "မြန်မာဘာသာဖြင့် ပြောဆိုထားတဲ့",
        "မြန်မာဘာသာဖြင့် ရေးသားထားတဲ့",
    )

    for prefix in unwanted_starts:
        if text.startswith(prefix):
            first_break = text.find("\n")
            if first_break != -1:
                text = text[first_break + 1:].strip()

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    unique = []
    seen = set()

    for paragraph in paragraphs:
        key = " ".join(paragraph.split()).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(paragraph)

    return "\n\n".join(unique).strip()


def generate_script(request: GenerateScriptRequest, story_context: dict | None = None) -> GenerateScriptResponse:
    video_id = extract_video_id(request.url)

    transcript_data = fetch_transcript(video_id)
    transcript = transcript_data["transcript"]

    prompt = build_prompt(request, transcript, story_context)

    script = None
    provider = None
    errors = []

    # Primary: Gemini
    try:
        script = call_gemini(prompt)
        provider = "Gemini"
        print("[generate-script] Gemini generation succeeded.", flush=True)
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        print(
            f"[generate-script] Gemini failed: {error_message}",
            flush=True,
        )
        errors.append(f"Gemini: {error_message}")

    # Fallback: Groq
    if not script:
        try:
            script = call_groq(prompt)
            provider = "Groq"
            print("[generate-script] Groq fallback succeeded.", flush=True)
        except Exception as exc:
            error_message = f"{type(exc).__name__}: {exc}"
            print(
                f"[generate-script] Groq failed: {error_message}",
                flush=True,
            )
            errors.append(f"Groq: {error_message}")

    # Fallback: Cohere
    if not script:
        try:
            script = call_cohere(prompt)
            provider = "Cohere"
            print("[generate-script] Cohere fallback succeeded.", flush=True)
        except Exception as exc:
            error_message = f"{type(exc).__name__}: {exc}"
            print(
                f"[generate-script] Cohere failed: {error_message}",
                flush=True,
            )
            errors.append(f"Cohere: {error_message}")

    if not script:
        raise RuntimeError(
            "All AI providers failed. " + " | ".join(errors)
        )

    script = clean_script(script)

    if not script:
        raise RuntimeError("AI returned an empty script after cleanup.")

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
