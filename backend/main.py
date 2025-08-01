from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from routes import projects  
from routes.chat import router as chat_router
from routes.meetings import router as meetings_router
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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects.router)
app.include_router(chat_router)
app.include_router(meetings_router)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
