from google import genai

from backend.config import GEMINI_API_KEY
from backend.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ScriptSegment,
)
from backend.services.analyzer import extract_video_id, fetch_transcript


def build_prompt(request: GenerateScriptRequest, transcript: str) -> str:
    return f"""
You are G.I Burmese AI, a professional Burmese content writer.

Create a natural Burmese narration script from the YouTube transcript below.

Requirements:
- Output language: {request.outputLanguage}
- Content type: {request.contentType}
- Script length: {request.scriptLength}
- Narration style: {request.narrationStyle}
- Do not invent facts that are not supported by the transcript.
- Rewrite naturally; do not simply translate word-for-word.
- Make the narration suitable for a Burmese YouTube video.
- Use clear Burmese Unicode.
- Avoid unnecessary English unless it is a proper name or technical term.

YouTube transcript:
{transcript}
"""


def generate_script(request: GenerateScriptRequest) -> GenerateScriptResponse:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured on the backend."
        )

    video_id = extract_video_id(request.url)
    transcript_data = fetch_transcript(video_id)
    transcript = transcript_data["transcript"]

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_prompt(request, transcript),
    )

    script = (response.text or "").strip()

    if not script:
        raise RuntimeError("Gemini returned an empty script.")

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
            "Real YouTube transcript processed by Gemini "
            "for Burmese script generation."
        ),
    )
