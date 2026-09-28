from pathlib import Path
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
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
from backend.services.recap.pipeline import create_job, get_job, BASE_DIR
from backend.services.recap.renderer import render_recap


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


@app.post("/api/recap/{job_id}/media")
async def upload_recap_media(
    job_id: str,
    file: UploadFile = File(...),
):
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Recap job not found.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No media filename provided.",
        )

    allowed_extensions = {
        ".mp4",
        ".mov",
        ".mkv",
        ".webm",
        ".avi",
    }

    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported video format. "
                "Allowed: mp4, mov, mkv, webm, avi."
            ),
        )

    job_dir = BASE_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    media_path = job_dir / f"authorized_media{suffix}"

    try:
        with media_path.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                output.write(chunk)

    except Exception as exc:
        if media_path.exists():
            media_path.unlink()

        print(
            f"[recap-media:{job_id}] "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Media upload failed: {type(exc).__name__}: {exc}",
        ) from exc

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "media_path": str(media_path),
        "message": "Authorized media uploaded successfully.",
    }


@app.post("/api/recap/{job_id}/render")
async def render_recap_video(job_id: str):
    job = get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Recap job not found.",
        )

    job_dir = BASE_DIR / job_id

    media_candidates = sorted(
        job_dir.glob("authorized_media.*")
    )

    if not media_candidates:
        raise HTTPException(
            status_code=400,
            detail="Authorized media has not been uploaded.",
        )

    media_path = media_candidates[0]

    try:
        result = render_recap(
            job_dir=job_dir,
            media_path=media_path,
        )

        return {
            "success": True,
            "job_id": job_id,
            "status": result.get("status"),
            "video": result.get("output"),
            "duration_seconds": result.get("duration_seconds"),
            "segments": result.get("segments", 0),
            "message": "Video rendered successfully."
            if result.get("status") == "complete"
            else result.get("reason"),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"[recap-render:{job_id}] {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Video render failed: {type(exc).__name__}: {exc}",
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


@app.get("/api/recap/{job_id}/video")
async def get_recap_video(job_id: str):
    job_dir = BASE_DIR / job_id
    video_path = job_dir / "final_recap.mp4"

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Rendered recap video not found.",
        )

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="GI-recap.mp4",
    )
