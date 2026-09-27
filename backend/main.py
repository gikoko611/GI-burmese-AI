from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import FRONTEND_ORIGINS
from backend.schemas import (
    AnalyzeVideoRequest,
    AnalyzeVideoResponse,
    GenerateScriptRequest,
    GenerateScriptResponse,
    RecapRequest,
    RecapJobResponse,
    RecapStatusResponse,
)
from backend.services.analyzer import analyze_video
from backend.services.script_generator import generate_script
from backend.services.recap.pipeline import create_job, get_job


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
        print(
            f"[generate-script] {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Script generation failed: {type(exc).__name__}: {exc}",
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


@app.post("/api/recap", response_model=RecapJobResponse)
async def create_recap(request: RecapRequest):
    try:
        job_id = create_job(
            request.url,
            request.language,
        )

        return RecapJobResponse(
            success=True,
            job_id=job_id,
            status="queued",
            message="Recap job started.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[recap] {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create recap job: {type(exc).__name__}: {exc}",
        ) from exc


@app.get("/api/recap/{job_id}", response_model=RecapStatusResponse)
async def recap_status(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Recap job not found.",
        )

    return RecapStatusResponse(
        success=True,
        job_id=job["job_id"],
        status=job["status"],
        step=job.get("step"),
        progress=job.get("progress", 0),
        message=job.get("message"),
        result=job.get("result"),
        error=job.get("error"),
    )
