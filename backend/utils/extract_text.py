# import os
# import textract
# import fitz

# def extract_text_from_file(file_path: str) -> str:
#     """
#     Extracts text from common document types like PDF, DOCX, PPTX, etc.
#     """
#     try:
#         # Uses textract to extract content
#         text = textract.process(file_path)
#         return text.decode('utf-8')
#     except Exception as e:
#         print(f"[ERROR] Failed to extract from {file_path}: {e}")
#         return ""

#for pdf format
# def extract_text_from_file(file_path: str) -> str:
#     try:
#         doc = fitz.open(file_path)
#         text = ""
#         for page in doc:
#             text += page.get_text()
#         return text
#     except Exception as e:
#         print(f"[ERROR] Failed to read {file_path}: {e}")
#         return ""

import docx2txt
from docx import Document

import os

def extract_text_from_file(path="Project_Overview.docx"):
    print("📂 Checking file path:", path)
    print("📂 Absolute path:", os.path.abspath(path))
    print("📂 File exists?", os.path.exists(path))
    
    try:
        doc = Document(path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        print("✅ Extracted paragraphs:", len(full_text))
        return "\n".join(full_text)
    except Exception as e:
        print("❌ Error reading file:", e)
        return ""