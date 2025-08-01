from .context_builder import build_context
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from utils.vector_store import search_similar_chunks
from utils.embedding import embed_text
from utils.llm_response import generate_response_stream
from utils.extract_text import extract_text_from_file
from qdrant_client import QdrantClient
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi.concurrency import run_in_threadpool
import os, re, requests, asyncio

load_dotenv()
router = APIRouter()

# ─── PRELOAD DOCX ONCE ─────────────────────────────────────────────────────
import os
from utils.s3_utils import upload_to_s3
from utils.extract_text import extract_text_from_file

DOC_LOCAL_PATH = os.path.join(os.getcwd(), "Project_Overview.docx")
S3_KEY = "uploads/Project_Overview.docx"

try:
    if upload_to_s3(DOC_LOCAL_PATH, S3_KEY):
        GLOBAL_DOC_CONTEXT = extract_text_from_file(DOC_LOCAL_PATH)
        print(f"✅ Uploaded and preloaded context ({len(GLOBAL_DOC_CONTEXT)} chars)")
    else:
        GLOBAL_DOC_CONTEXT = ""
except Exception as e:
    GLOBAL_DOC_CONTEXT = ""
    print(f"⚠️ Error during upload/preload: {e}")

# Qdrant & Supabase clients
aqdrant = QdrantClient(host="localhost", port=6333)
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8001")

# Patterns
TIME_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}(?:,\s*\d{4})?(?:\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)?\b", re.IGNORECASE)
YES_RE = re.compile(r"^(?:yes|yeah|yup|sure)$", re.IGNORECASE)
CONFUSION_RE = re.compile(r"\b(?:didn['’]?t understand|not clear|confused|explain again|repeat)\b", re.IGNORECASE)

class ChatQuery(BaseModel):
    project_name: str
    query: str

@router.post("/chat/stream")
async def chat_stream(data: ChatQuery):
    project_name = data.project_name or "Smart Traffic AI"
    text = data.query.strip()
    print("hiiii")

    print(f"Project: {project_name}")
    print(f"Query: {text}")

    # Confusion fallback
    if len(text) < 500 and CONFUSION_RE.search(text):
        print("yess")
        return StreamingResponse(
            iter(["🤖 It seems this wasn’t clear. Would you like me to schedule a meeting?"]),
            media_type="text/plain"
        )

    # Placeholder for meeting logic (no user id now)
    if len(text) < 100 and YES_RE.match(text):
        print("nooo")
        meeting_time = datetime.now() + timedelta(hours=1)
        payload = {
            "project_name": project_name,
            "requested_time": meeting_time.strftime('%Y-%m-%d %H:%M:%S'),
            "team_member_email": "placeholder@example.com"  # required for your backend? Replace or remove
        }
        try:
            print("ssssss")
            resp = requests.post(f"{API_URL}/api/schedule_meeting", json=payload, timeout=5)
            resp.raise_for_status()
            result = resp.json()
            reply = result.get("message", "Meeting scheduled.")
            if result.get("join_url"):
                reply += f"\nJoin here: {result['join_url']}"
            return StreamingResponse(iter([reply]), media_type="text/plain")
        except requests.RequestException as e:
            return StreamingResponse(iter([f"⚠️ Scheduling error: {str(e)}"]), media_type="text/plain")

    # Main response
    try:
        print("byeee")
        # Remove email – just build context from project and query
        context = await build_context(project_name, text)

        async def stream_and_store():
            full_answer = ""
            for chunk in generate_response_stream(context, text):
                full_answer += chunk
                yield chunk
            # Save to Supabase without user_id
            asyncio.create_task(save_to_supabase(project_name, data.query, full_answer))

        return StreamingResponse(stream_and_store(), media_type="text/plain")

    except Exception as e:
        print("mmmmmm")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/voice")
async def chat_voice_endpoint(data: ChatQuery):
    try:
        query = data.query.strip()
        user_email = data.email.lower()
        project_name = data.project_name or "Smart Traffic AI"

        # Use preloaded DOCX context
        context = GLOBAL_DOC_CONTEXT
        if not context:
            context = extract_text_from_file(_DOC_PATH)

        embedding = await run_in_threadpool(embed_text, query)
        full_response = "".join(generate_response_stream(context, query))

        # fire-and-forget save
        asyncio.create_task(save_to_supabase(user_email, project_name, query, full_response))

        return JSONResponse(content={"reply": full_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime

async def save_to_supabase(project_name: str, query: str, response: str):
    try:
        payload = {
            "project_name": project_name,
            "query": query,
            "response": response,
            "created_at": datetime.utcnow().isoformat()
        }

        result = supabase.table("chats").insert(payload).execute()

        if result.status_code in [200, 201]:
            print("✅ Chat log saved successfully.")
        else:
            print("⚠️ Failed to save chat log to Supabase.")

    except Exception as e:
        print(f"❌ Error while saving chat log: {str(e)}")
