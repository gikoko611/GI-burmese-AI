from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import FRONTEND_ORIGINS
from backend.schemas import (
    AnalyzeVideoRequest,
    AnalyzeVideoResponse,
    GenerateScriptRequest,
    GenerateScriptResponse,
)
from backend.services.analyzer import analyze_video
from backend.services.script_generator import generate_script


app = FastAPI(
    title="G.I Burmese AI Backend",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "G.I Burmese AI Backend",
    }


@app.post("/api/generate-script", response_model=GenerateScriptResponse)
async def generate_burmese_script(request: GenerateScriptRequest):
    try:
        return generate_script(request)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Script generation failed.",
        ) from exc


@app.get("/")
async def root():
    return {
        "message": "G.I Burmese AI Backend is running",
    }


@app.post("/api/analyze", response_model=AnalyzeVideoResponse)
async def analyze(request: AnalyzeVideoRequest):
    try:
        result = analyze_video(request.url)

        return AnalyzeVideoResponse(
            success=True,
            analysis=result,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Video analysis failed.",
        ) from exc
