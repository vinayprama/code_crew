from fastapi import APIRouter, HTTPException
from utils.vector_store import add_doc_to_vector_store
from utils.extract_text import extract_text_from_file
from utils.s3_utils import check_project_exists_in_s3
import os

router = APIRouter()

@router.get('/projects/{project_name}')
def initialize_chat(project_name: str):
    s3_folder = f"code_crew/{project_name.strip().replace(' ', '_')}"

    # Check if project folder exists in S3
    if not check_project_exists_in_s3(s3_folder):
        raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found in S3")

    # Use a sample file path to simulate local vector indexing (if needed)
    file_path = os.path.join(os.getcwd(), "Project_Overview.docx")
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
