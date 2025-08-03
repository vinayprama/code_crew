# from fastapi import APIRouter, File, UploadFile, Form, HTTPException
# from fastapi.responses import JSONResponse
# from utils.extract_text import extract_text_from_file
# from utils.s3_utils import upload_to_s3, check_project_exists_in_s3
# from uuid import uuid4
# import os
# import shutil

# router = APIRouter()

# @router.post("/upload_doc/")
# async def upload_doc(
#     file: UploadFile = File(...),
#     project_name: str = Form(...)
# ):
#     if not file.filename.endswith(".docx"):
#         raise HTTPException(status_code=400, detail="Only DOCX files are supported.")

#     s3_folder = f"code_crew/{project_name.strip().replace(' ', '_')}"

#     # 1. Check if project folder already exists in S3
#     if check_project_exists_in_s3(s3_folder):
#         return JSONResponse(status_code=200, content={
#             "message": f"📁 Project '{project_name}' already exists. Save here?",
#             "project_exists": True
#         })

#     # 2. Save temporarily
#     temp_path = f"temp_{uuid4().hex}.docx"
#     with open(temp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 3. Upload to S3
#     try:
#         s3_key = f"{s3_folder}/{file.filename}"
#         upload_success = upload_to_s3(temp_path, s3_key)
#         os.remove(temp_path)

#         if not upload_success:
#             raise Exception("Upload failed")

#         return JSONResponse(status_code=200, content={
#             "message": f"✅ Uploaded to S3 at '{s3_key}'",
#             "project_exists": False
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from utils.extract_text import extract_text_from_file
from utils.s3_utils import upload_to_s3, check_project_exists_in_s3
from uuid import uuid4
import os
import shutil

router = APIRouter()

# 🔥 NEW ROUTE HERE
@router.get("/upload/check_project/{project_name}")
def check_project_exists(project_name: str):
    s3_folder = f"code_crew/{project_name.strip().replace(' ', '_')}"
    exists = check_project_exists_in_s3(s3_folder)
    return JSONResponse(content={"exists": exists})

@router.post("/upload_doc/")
async def upload_doc(
    file: UploadFile = File(...),
    project_name: str = Form(...)
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files are supported.")

    s3_folder = f"code_crew/{project_name.strip().replace(' ', '_')}"

    if check_project_exists_in_s3(s3_folder):
        return JSONResponse(status_code=200, content={
            "message": f"📁 Project '{project_name}' already exists. Save here?",
            "project_exists": True
        })

    temp_path = f"temp_{uuid4().hex}.docx"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        s3_key = f"{s3_folder}/{file.filename}"
        upload_success = upload_to_s3(temp_path, s3_key)
        os.remove(temp_path)

        if not upload_success:
            raise Exception("Upload failed")

        return JSONResponse(status_code=200, content={
            "message": f"✅ Uploaded to S3 at '{s3_key}'",
            "project_exists": False
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
