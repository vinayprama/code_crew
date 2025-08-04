from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from utils.s3_utils import download_from_s3, upload_to_s3
import whisper
import os
import tempfile

router = APIRouter()

@router.post("/transcribe_video/")
async def transcribe_video(s3_key: str = Form(...), project_name: str = Form(...)):
    try:
        # Step 1: Download video from S3
        local_path = tempfile.mktemp(suffix=".mp4")
        success = download_from_s3(s3_key, local_path)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to download video from S3.")

        # Step 2: Transcribe
        model = whisper.load_model("base")
        result = model.transcribe(local_path)
        transcription = result["text"]

        # Step 3: Save transcription to .txt and upload to S3
        txt_path = tempfile.mktemp(suffix=".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcription)

        s3_text_key = f"code_crew/{project_name.strip().replace(' ', '_')}/transcripts/{os.path.basename(s3_key)}.txt"
        uploaded = upload_to_s3(txt_path, s3_text_key)
        os.remove(local_path)
        os.remove(txt_path)

        if not uploaded:
            raise Exception("Failed to upload transcription to S3")

        return JSONResponse(status_code=200, content={
            "message": "✅ Transcription complete and saved to S3.",
            "transcription": transcription,
            "transcript_s3_key": s3_text_key
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
