from utils.extract_text import extract_text_from_file
from utils.vector_store import init_collection, add_doc_to_vector_store
from utils.embedding import embed_text

file_path = r"C:\Users\Prama\Documents\ai1\Project_Overview.docx"
collection_name = "project_docs"

def prepare_and_upload():
    try:
        # Step 1: Extract
        print("[INFO] Extracting text...")
        text = extract_text_from_file(file_path)
        print(f"[INFO] Extracted length: {len(text)}")

        if not text.strip():
            print("[ERROR] No text extracted from the DOCX file.")
            return

        # Step 2: Chunking
        print("[INFO] Splitting text into chunks...")
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        print(f"[INFO] Total chunks: {len(chunks)}")

        # Step 3: Create metadata payloads (required by your vector_store function)
        metadata_chunks = [{"text": chunk} for chunk in chunks]

        # Step 4: Initialize Qdrant collection
        print("[INFO] Initializing Qdrant collection...")
        init_collection(collection_name)

        # Step 5: Embed and upload chunks
        add_doc_to_vector_store(chunks, metadata_chunks)

        print("[SUCCESS] Document uploaded and indexed in Qdrant.")

    except Exception as e:
        print(f"[FAIL] {e}")

if __name__ == "__main__":
    prepare_and_upload()
