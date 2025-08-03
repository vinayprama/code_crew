

from .context_builder import build_context
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from utils.llm_response import generate_response_stream
from datetime import datetime, timedelta
from utils.s3_utils import upload_to_s3
from utils.extract_text import extract_text_from_file
import os, re, requests, asyncio

router = APIRouter()

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")

# Regex matchers
TIME_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?)|(?:Jan|Feb|Mar|...)\b", re.IGNORECASE)
YES_RE = re.compile(r"^(?:yes|yeah|yup|sure)$", re.IGNORECASE)
CONFUSION_RE = re.compile(r"\b(?:didn['’]?t understand|not clear|confused|explain again|repeat)\b", re.IGNORECASE)

class ChatQuery(BaseModel):
    project_name: str
    query: str

class VoiceQuery(BaseModel):
    project_name: str
    query: str

@router.post("/chat/stream")
async def chat_stream(data: ChatQuery):
    project_name = data.project_name or "Smart Traffic AI"
    text = data.query.strip()

    print(f"Project: {project_name}\nQuery: {text}")

    if len(text) < 500 and CONFUSION_RE.search(text):
        return StreamingResponse(
            iter(["🤖 It seems this wasn’t clear. Would you like me to schedule a meeting?"]),
            media_type="text/plain"
        )

    if len(text) < 100 and YES_RE.match(text):
        meeting_time = datetime.now() + timedelta(hours=1)
        payload = {
            "project_name": project_name,
            "requested_time": meeting_time.strftime('%Y-%m-%d %H:%M:%S'),
            "team_member_email": "placeholder@example.com"
        }
        try:
            resp = requests.post(f"{API_URL}/api/schedule_meeting", json=payload, timeout=5)
            resp.raise_for_status()
            result = resp.json()
            reply = result.get("message", "Meeting scheduled.")
            if result.get("join_url"):
                reply += f"\nJoin here: {result['join_url']}"
            return StreamingResponse(iter([reply]), media_type="text/plain")
        except requests.RequestException as e:
            return StreamingResponse(iter([f"⚠️ Scheduling error: {str(e)}"]), media_type="text/plain")

    try:
        context = await build_context(project_name, text)

        async def stream_response():
            for chunk in generate_response_stream(context, text):
                yield chunk

        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/voice")
async def chat_voice(data: VoiceQuery):
    try:
        context = await build_context(data.project_name, data.query)
        full_response = ""
        for chunk in generate_response_stream(context, data.query):
            full_response += chunk
        return {"reply": full_response.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice chat error: {str(e)}")
