from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import projects  
from routes.chat import router as chat_router
from routes.meetings import router as meetings_router
from routes.upload_doc import router as upload_doc_router
from routes.transcribe_video import router as transcribe_video_router
from routes.upload_doc import router as upload_video_router  # reused router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",  # React dev
    "http://127.0.0.1:5500",  # static HTML
    "*"                      # production flexibility
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or set frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
# app.include_router(auth_router)
app.include_router(projects.router)
app.include_router(chat_router)
app.include_router(meetings_router)
app.include_router(upload_doc_router)  
app.include_router(upload_video_router)
app.include_router(transcribe_video_router)


# Load S3 config from .env
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
