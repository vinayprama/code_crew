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