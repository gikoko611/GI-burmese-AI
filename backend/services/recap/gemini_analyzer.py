import json
import os
import time
import urllib.error
import urllib.request
from typing import List

from pydantic import BaseModel, Field

from backend.config import GEMINI_API_KEY


class Character(BaseModel):
    id: str
    name: str
    role: str = "supporting"
    description: str = ""
    voice_profile: str = "neutral"


class Scene(BaseModel):
    id: str
    order: int
    title: str
    summary: str
    characters: List[str] = Field(default_factory=list)
    important: bool = True


class StoryEvent(BaseModel):
    order: int
    scene_id: str
    event: str
    consequence: str = ""


class StoryAnalysis(BaseModel):
    title: str
    genre: str = "unknown"
    premise: str = ""
    characters: List[Character] = Field(default_factory=list)
    scenes: List[Scene] = Field(default_factory=list)
    events: List[StoryEvent] = Field(default_factory=list)
    conflict: str = ""
    ending: str = ""
    recap_focus: List[str] = Field(default_factory=list)


def _schema():
    return {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "genre": {"type": "STRING"},
            "premise": {"type": "STRING"},
            "characters": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "STRING"},
                        "name": {"type": "STRING"},
                        "role": {"type": "STRING"},
                        "description": {"type": "STRING"},
                        "voice_profile": {"type": "STRING"},
                    },
                    "required": [
                        "id",
                        "name",
                        "role",
                        "description",
                        "voice_profile",
                    ],
                },
            },
            "scenes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "STRING"},
                        "order": {"type": "INTEGER"},
                        "title": {"type": "STRING"},
                        "summary": {"type": "STRING"},
                        "characters": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                        },
                        "important": {"type": "BOOLEAN"},
                    },
                    "required": [
                        "id",
                        "order",
                        "title",
                        "summary",
                        "characters",
                        "important",
                    ],
                },
            },
            "events": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "order": {"type": "INTEGER"},
                        "scene_id": {"type": "STRING"},
                        "event": {"type": "STRING"},
                        "consequence": {"type": "STRING"},
                    },
                    "required": [
                        "order",
                        "scene_id",
                        "event",
                        "consequence",
                    ],
                },
            },
            "conflict": {"type": "STRING"},
            "ending": {"type": "STRING"},
            "recap_focus": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
            },
        },
        "required": [
            "title",
            "genre",
            "premise",
            "characters",
            "scenes",
            "events",
            "conflict",
            "ending",
            "recap_focus",
        ],
    }


def analyze_story_with_gemini(
    transcript: str,
    title: str = "",
) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    primary_model = os.getenv(
        "GEMINI_ANALYZER_MODEL",
        "gemini-3.8-flash",
    )

    fallback_models = [
        primary_model,
        "gemini-3.7-flash",
        "gemini-3.6-flash",
    ]

    prompt = f"""
You are the story-analysis engine for G.I Movie Recap.

Analyze the supplied video transcript as a STORY, not as a generic
article or educational explanation.

Reconstruct the narrative in chronological order.

Rules:
- Identify important characters.
- Give every important character a stable id.
- Infer each character's narrative role.
- Assign voice_profile as one of:
  male, female, child, elderly_male, elderly_female, neutral
- Only infer gender/age when reasonably supported by the text.
- Otherwise use neutral.
- Divide the story into meaningful chronological scenes.
- Extract major events and their consequences.
- Identify the central conflict.
- Explain the ending if it is present.
- Preserve names and important factual details.
- Do not invent scenes not supported by the transcript.
- Do not write a generic review.
- Do not reproduce long passages from the source.
- The output will be used to generate a Burmese movie recap.

Source title:
{title or "Unknown"}

Transcript:
{transcript}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _schema(),
        },
    }

    last_error = None

    for model in fallback_models:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent"
        )

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            },
            method="POST",
        )

        for attempt in range(3):
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=120,
                ) as response:
                    raw = response.read().decode("utf-8")
                    break

            except urllib.error.HTTPError as exc:
                body = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )

                last_error = (
                    f"Gemini API HTTP {exc.code}: {body}"
                )

                if exc.code == 503:
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue

                    break

                if exc.code in (429, 500, 502, 504):
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue

                    break

                raise RuntimeError(last_error) from exc

            except urllib.error.URLError as exc:
                last_error = (
                    f"Gemini API connection failed: {exc.reason}"
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                break

        else:
            continue

        if "raw" in locals():
            break

    else:
        raise RuntimeError(
            last_error or "Gemini API request failed."
        )

    try:
        data = json.loads(raw)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Unexpected Gemini response: {raw[:2000]}"
        ) from exc

    try:
        analysis = StoryAnalysis.parse_raw(text)
    except Exception as exc:
        raise RuntimeError(
            f"Gemini returned invalid structured output: {exc}"
        ) from exc

    return json.loads(analysis.json())
