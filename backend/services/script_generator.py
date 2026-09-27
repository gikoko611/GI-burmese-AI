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
- Write in fluent, natural Myanmar Burmese (မြန်မာစာ) suitable for spoken narration.
- Do NOT translate sentence-by-sentence or word-for-word.
- Use normal conversational Burmese grammar and natural Myanmar vocabulary.
- Avoid awkward literal translations and unnatural phrases.
- Avoid filler phrases such as "ဒီနားထောင်ထားတဲ့ သူငယ်ချင်းတွေ", "ထိပ်တန်းမြှောက်ရေးမယ်", or similar machine-translated wording.
- Preserve important names, places, events, and facts from the source.
- Do not invent facts that are not supported by the transcript.
- For movie/story recap, summarize the story clearly in chronological order.
- Focus on the important events, characters, conflict, and outcome.
- Write as if an experienced Burmese YouTube narrator is explaining the content to viewers.
- Do not reproduce long passages of the original transcript or song lyrics.
- For songs, summarize the meaning and theme instead of reproducing lyrics.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Return only the finished narration script.
- Do not start with meta text such as "ဒီစာတမ်းကို..." or "မြန်မာဘာသာဖြင့်..."
- Do not repeat the same sentence or idea multiple times.
- Avoid generic filler and artificial phrases.
- Prefer concise, human-sounding Burmese narration.
- Do not structure the answer into artificial "အစပိုင်း / အလယ်ပိုင်း / နောက်ဆုံးပိုင်း" sections unless the source actually requires it.

TRANSCRIPT:
{transcript}
""".strip()


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
        print("[generate-script] Groq generation succeeded.", flush=True)
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
