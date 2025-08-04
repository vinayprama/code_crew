from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from utils.s3_utils import download_from_s3
from uuid import uuid4
import os
import whisper

router = APIRouter()
model = whisper.load_model("base")  # You can use "small", "medium", or "large" if you want better accuracy

@router.get("/transcribe_video/")
async def transcribe_video(s3_key: str = Query(...)):
    local_path = f"temp_{uuid4().hex}_{os.path.basename(s3_key)}"

    try:
        # Download from S3
        if not download_from_s3(s3_key, local_path):
            raise HTTPException(status_code=500, detail="Failed to download video from S3")

        # Transcribe with Whisper
        result = model.transcribe(local_path)
        os.remove(local_path)

        return JSONResponse(status_code=200, content={"transcription": result["text"]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
