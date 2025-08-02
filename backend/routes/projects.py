from fastapi import FastAPI, HTTPException, Depends,APIRouter,UploadFile, File, Form
from pydantic import BaseModel, HttpUrl
from supabase import create_client, Client
from postgrest.exceptions import APIError
from utils.vector_store import init_collection
import os
from uuid import uuid4
from typing import Optional
from datetime import datetime
from utils.vector_store import add_doc_to_vector_store
from utils.extract_text import extract_text_from_file
# from utils.sharepoint import fetch_sharepoint_docs
#vectordb
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()  

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
FERNET_KEY = os.getenv('FERNET_KEY')

# Initialize Supabase client and Fernet client and Fernet
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
fernet = Fernet(FERNET_KEY)
router = APIRouter()

# Pydantic schema for project creation
class ProjectCreate(BaseModel):
    project_name: str
    sharepoint_link: HttpUrl
    sharepoint_username: str
    sharepoint_password: str


@router.post('/api/projects', status_code=201)
def create_project(payload: ProjectCreate, user_id: Optional[str] = None):
    # Check if project already exists
    existing = supabase.table('projects') \
        .select('id') \
        .eq('project_name', payload.project_name) \
        .limit(1).execute()
    
    if existing.data:
        raise HTTPException(status_code=400, detail='Project with this name already exists') 

    # Encrypt password
    encrypted_pw = fernet.encrypt(payload.sharepoint_password.encode()).decode()

    # Create project record
    project_id = str(uuid4())
    record = {
        'id': project_id,
        'project_name': payload.project_name,
        'sharepoint_link': str(payload.sharepoint_link),
        'sharepoint_username': payload.sharepoint_username,
        'sharepoint_password': encrypted_pw,
       
    }

    try:
        response = supabase.table("projects").insert(record).execute()
        
        if response.status_code not in [200, 201]:
            raise HTTPException(status_code=500, detail="Failed to create project in Supabase")

        print("Project inserted:", response.data)
        return {"message": "Project created successfully", "data": response.data}

    except APIError as e:
        raise HTTPException(status_code=500, detail=f"Supabase API error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#local dox code
@router.get('/projects/{project_name}')
def initialize_chat(project_name: str):
    # 1. Check if project exists in Supabase
    result = supabase.table('projects').select("*").eq("project_name", project_name).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Set correct single .docx file path
    file_path = "C:/Users/Prama/Documents/ai1/Project_Overview.docx"

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=500, detail=f"File not found: {file_path}")

    try:
        text = extract_text_from_file(file_path)
        metadata = {
            "project_name": project_name,
            "file_path": file_path,
        }

        add_doc_to_vector_store([text], [metadata])

        return {"message": "1 document processed and ready for chat."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
