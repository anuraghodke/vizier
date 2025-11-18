"""
API routes for animation generation endpoints.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import shutil
import zipfile
import io
from typing import List

from app.models.schemas import GenerateResponse, JobStatus
from app.workers.celery_worker import generate_frames_task
from app.job_store import job_store

router = APIRouter()

# Directories
UPLOADS_DIR = Path("uploads")
OUTPUTS_DIR = Path("outputs")


@router.post("/generate", response_model=GenerateResponse)
async def generate_animation(
    frame1: UploadFile = File(..., description="First keyframe (PNG)"),
    frame2: UploadFile = File(..., description="Second keyframe (PNG)"),
    instruction: str = Form(..., description="Natural language animation instruction")
):
    """
    Upload two keyframes and instruction to generate intermediate frames.

    - **frame1**: First keyframe PNG file
    - **frame2**: Second keyframe PNG file
    - **instruction**: Natural language description (e.g., "create 8 bouncy frames")

    Returns job_id for tracking progress.
    """
    # Validate file types
    if not frame1.filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="frame1 must be a PNG file")
    if not frame2.filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="frame2 must be a PNG file")

    # Validate instruction
    if len(instruction.strip()) < 5:
        raise HTTPException(status_code=400, detail="Instruction must be at least 5 characters")
    if len(instruction.strip()) > 500:
        raise HTTPException(status_code=400, detail="Instruction must be less than 500 characters")

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save uploaded files
    UPLOADS_DIR.mkdir(exist_ok=True)
    frame1_path = UPLOADS_DIR / f"{job_id}_frame1.png"
    frame2_path = UPLOADS_DIR / f"{job_id}_frame2.png"

    with open(frame1_path, "wb") as f:
        shutil.copyfileobj(frame1.file, f)

    with open(frame2_path, "wb") as f:
        shutil.copyfileobj(frame2.file, f)

    # Initialize job status
    job_store[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "stage": None,
        "frames": None,
        "params": None,
        "error": None
    }

    # Queue Celery task
    generate_frames_task.delay(
        job_id=job_id,
        frame1_path=str(frame1_path),
        frame2_path=str(frame2_path),
        instruction=instruction
    )

    return GenerateResponse(job_id=job_id, status="pending")


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Poll job status and progress.

    - **job_id**: Unique job identifier

    Returns current job status, progress, and generated frames if complete.
    """
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(**job_store[job_id])


@router.get("/frames/{job_id}/{frame_name}")
async def get_frame(job_id: str, frame_name: str):
    """
    Serve individual generated frame as PNG.

    - **job_id**: Unique job identifier
    - **frame_name**: Frame filename (e.g., "frame_001.png")

    Returns PNG image file.
    """
    frame_path = OUTPUTS_DIR / job_id / frame_name

    if not frame_path.exists():
        raise HTTPException(status_code=404, detail="Frame not found")

    return FileResponse(
        path=frame_path,
        media_type="image/png",
        filename=frame_name
    )


@router.get("/download/{job_id}")
async def download_frames(job_id: str):
    """
    Download all generated frames as a ZIP archive.

    - **job_id**: Unique job identifier

    Returns ZIP file containing all frames.
    """
    job_output_dir = OUTPUTS_DIR / job_id

    if not job_output_dir.exists():
        raise HTTPException(status_code=404, detail="Job output not found")

    # Check if job is complete
    if job_id not in job_store or job_store[job_id]["status"] != "complete":
        raise HTTPException(status_code=400, detail="Job not complete yet")

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add all PNG files from job output directory
        for frame_file in sorted(job_output_dir.glob("*.png")):
            zip_file.write(frame_file, arcname=frame_file.name)

    zip_buffer.seek(0)

    return FileResponse(
        path=None,
        media_type="application/zip",
        filename=f"vizier_{job_id}.zip",
        content=zip_buffer.getvalue()
    )
