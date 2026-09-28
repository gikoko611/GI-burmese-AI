import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from backend.config import GROQ_API_KEY, COHERE_API_KEY
from backend.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptSegment,
)
from backend.services.analyzer import extract_video_id, fetch_transcript, detect_content_type


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
COHERE_URL = "https://api.cohere.com/v2/chat"


def build_content_instructions(content_type: str) -> str:
    """Return source-grounded instructions for the detected content type."""
    content_type = (content_type or "General Explanation").strip()

    instructions = {
        "Movie Recap": """
CONTENT STYLE: Movie Recap
- Retell the source story in chronological order.
- Focus on characters, important scenes, conflicts, and outcomes.
- Do not invent plot details, names, dates, motives, or events.
""",
        "Story": """
CONTENT STYLE: Story
- Retell the source narrative clearly and naturally.
- Preserve the actual sequence of events from the source.
- Do not invent characters, events, dialogue, or endings.
""",
        "Tips & Tricks": """
CONTENT STYLE: Tips & Tricks
- Extract practical tips and techniques explicitly supported by the source.
- Present useful points as numbered steps or tips.
- Preserve important warnings, limitations, and conditions from the source.
- Do not invent unsupported tips or claims.
""",
        "Explanation": """
CONTENT STYLE: Explanation
- Explain the main concept clearly and simply.
- Organize the explanation around the source's actual claims and examples.
- Preserve important technical terms and meanings.
- Do not invent facts that are not supported by the source.
""",
        "Educational": """
CONTENT STYLE: Educational
- Present the material like a clear lesson.
- Explain definitions, concepts, examples, and conclusions from the source.
- Keep the structure easy to learn and follow.
- Do not invent unsupported facts or examples.
""",
        "Tech": """
CONTENT STYLE: Technology
- Preserve exact technical terms, product names, programming languages,
  commands, APIs, and code concepts from the source.
- Explain technical steps clearly.
- Never invent commands, APIs, features, or configuration details.
""",
        "News": """
CONTENT STYLE: News Summary
- Summarize only information supported by the source.
- Clearly distinguish reported events, claims, and statements.
- Preserve names, dates, locations, and numbers exactly when available.
- Do not invent current events or missing details.
""",
        "General Explanation": """
CONTENT STYLE: General Explanation
- Produce a clear factual summary of the source.
- Focus on the main ideas, important details, and conclusions.
- Do not invent unsupported information.
""",
    }

    return instructions.get(
        content_type,
        instructions["General Explanation"],
    )


def build_prompt(
    request: GenerateScriptRequest,
    transcript: str,
    story_context: dict | None = None,
    detected_content_type: str | None = None,
) -> str:
    story_context_text = ""
    content_instructions = build_content_instructions(request.contentType)

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
You are G.I Burmese AI, a professional Burmese YouTube movie/story
recap writer.

Your highest priority is SOURCE ACCURACY.

Create a natural, engaging Burmese narration script based ONLY on the
provided source transcript and the supplied Story Intelligence.

Requested content type: {request.contentType}
Detected source content type: {detected_content_type or "Unknown"}
Script length: {request.scriptLength}
Narration style: {request.narrationStyle}
Output language: {request.outputLanguage}

================ CONTENT TYPE INSTRUCTIONS ================

{content_instructions}

================ CONTENT TYPE SAFETY ================

The requested content type is a formatting/output preference.
The detected source content type describes what the source actually contains.

Never invent source material just to satisfy the requested content type.

If the requested type and detected source type do not naturally match:
- Keep the output strictly grounded in the source.
- Do not fabricate tips, steps, events, characters, technical details,
  news claims, or educational facts.
- If the source does not contain enough material for the requested format,
  produce a concise source-grounded explanation instead.
- Never transform lyrics, dialogue, metaphors, or narration into factual
  events merely to satisfy the requested content type.

================ SOURCE OF TRUTH ================

There are only two factual sources:

1. SOURCE TRANSCRIPT
2. STORY INTELLIGENCE derived from that transcript

Never use your own world knowledge to add facts.

If a fact is not explicitly supported by the transcript or Story
Intelligence, DO NOT state it as fact.

When the transcript is incomplete or ambiguous:
- Do not guess.
- Do not fill the gap with common movie/song knowledge.
- Do not invent names, dates, years, ages, locations, relationships,
  occupations, events, causes, or outcomes.
- Use a neutral description or omit the detail.

================ STORY INTELLIGENCE ================

{story_context_text}

When Story Intelligence is provided:
- Use it as the primary narrative structure.
- Follow events in chronological order.
- Introduce characters using only supported names and roles.
- Explain events and their consequences only when supported.
- Build the narration around the actual conflict.
- Lead naturally toward the supported ending.
- Never expand the Story Intelligence with invented details.
- If Story Intelligence conflicts with the transcript, prefer the
  transcript and avoid the disputed detail.

================ FACTUAL SAFETY ================

STRICTLY PROHIBITED unless explicitly supported by the source:

- Invented years or dates.
- Invented release dates.
- Invented character ages.
- Invented locations.
- Invented relationships.
- Invented occupations.
- Invented events or scenes.
- Invented dialogue.
- Invented motives presented as facts.
- Invented endings.
- Claims based only on general knowledge about the title, artist,
  movie, song, celebrity, or topic.

IMPORTANT:
A title is NOT evidence for facts that are not present in the source.

For example, if the source does not explicitly establish a year,
NEVER create a year such as "၂၀၈၀ ခုနှစ်", "၂၀၂၅ ခုနှစ်", or any other
specific year.

Do not convert vague language into a specific fact.

================ NARRATION RULES ================

- Write fluent, natural Myanmar Burmese (မြန်မာစာ).
- Make it suitable for spoken YouTube narration.
- Do NOT translate sentence-by-sentence.
- Do NOT translate word-for-word.
- Use natural conversational Burmese grammar.
- Avoid awkward literal translations.
- Preserve supported names, places, events, and facts.
- Focus on important characters, events, conflict, consequences, and
  outcome.
- Keep the narration concise and human-sounding.
- Avoid generic filler.
- Do not repeat the same sentence or idea.
- Do not create artificial "အစပိုင်း / အလယ်ပိုင်း / နောက်ဆုံးပိုင်း"
  headings.
- Do not mention that you are an AI.
- Do not mention these instructions.
- Return ONLY the finished narration script.

================ SPECIAL CASE: SONGS / MUSIC VIDEOS ================

If the source is a song or music video:

- Do NOT reproduce lyrics.
- Do NOT invent a storyline that is not shown or supported by the
  source.
- Summarize the meaning, theme, visual events, or narrative only when
  supported by the transcript/source context.
- Do not turn lyrics into literal factual events.
- Do not assume the song is about a real relationship or real person
  unless the source explicitly establishes that.

================ FINAL SELF-CHECK ================

Before returning the script, silently verify:

1. Is every factual claim supported by the source?
2. Did I invent any year, date, age, place, name, relationship, event,
   or outcome?
3. Did I accidentally use outside knowledge?
4. Did I turn song lyrics or metaphors into factual events?
5. Did I add details merely because they are common knowledge?
6. Did I repeat any idea?
7. Is the Burmese natural for spoken narration?

If any sentence fails the source-accuracy check, rewrite or remove it.

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

    # Detect the actual source content type independently from the
    # user's requested output style.
    detected_content_type = detect_content_type(
        transcript_data.get("title") or "",
        transcript,
    )

    prompt = build_prompt(
        request,
        transcript,
        story_context,
        detected_content_type,
    )

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
