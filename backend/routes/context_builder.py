# import os

# from utils.vector_store import add_doc_to_vector_store, search_similar_chunks
# from utils.embedding import embed_text
# import boto3
# from botocore.exceptions import BotoCoreError, ClientError
# # from utils.embeddings import embed_text, search_similar_chunks
# from starlette.concurrency import run_in_threadpool

# AWS_REGION = os.getenv("AWS_REGION")
# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# GLOBAL_DOC_CONTEXT = "This is fallback content. No project documents were found."

# s3_client = boto3.client(
#     "s3",
#     region_name=AWS_REGION,
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
# )

# def list_user_project_files(user_email: str, project_name: str):
#     prefix = f"{user_email}/{project_name}/"
#     try:
#         response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
#         return [item["Key"] for item in response.get("Contents", [])]
#     except (BotoCoreError, ClientError) as e:
#         print(f"⚠️ S3 list error: {e}")
#         return []

# def read_s3_file_content(key: str) -> str:
#     try:
#         response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
#         return response["Body"].read().decode("utf-8", errors="ignore")
#     except Exception as e:
#         print(f"❌ S3 read error {key}: {e}")
#         return ""

# from supabase import create_client
# import os
# from typing import List, Dict
# # from utils.vector_store import search_vector_store  # Assumed search function

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# async def build_context(project_name: str, query: str) -> str:
#     try:
#         # Step 1: Query projects table to confirm project exists
#         result = (
#             supabase.table("projects")
#             .select("project_name, context")  # Select specific columns to avoid fetching unnecessary data
#             .eq("project_name", project_name)
#             .execute()
#         )

#         # Check if exactly one project was found
#         if not result.data:
#             print(f"No project found for '{project_name}' in Supabase.")
#             return f"No project named '{project_name}' exists. Please upload a project or check the name."
#         if len(result.data) > 1:
#             print(f"Multiple projects found for '{project_name}' in Supabase.")
#             return f"Multiple projects named '{project_name}' found. Please ensure project names are unique."

#         # Project exists, get base context if available
#         project_data = result.data[0]
#         base_context = project_data.get("context", "")

#         # Step 2: Search vector store for relevant text chunks
#         try:
#             similar_chunks: List[Dict] = add_doc_to_vector_store(project_name, query)
#             if not similar_chunks:
#                 print(f"No matching chunks found in vector store for project '{project_name}' and query '{query}'.")
#                 return base_context or "(No matching documents found in vector store.)"

#             # Step 3: Build context from chunks
#             chunk_texts = [chunk.get("text", "") for chunk in similar_chunks if "text" in chunk]
#             context = "\n\n".join(chunk_texts) if chunk_texts else base_context
#             return context if context else "(No relevant content found.)"
#         except Exception as e:
#             print(f"Vector store search error: {str(e)}")
#             return base_context or f"Failed to search documents: {str(e)}"

#     except Exception as e:
#         print(f"Error in build_context: {str(e)}")
#         return f"Failed to build context: {str(e)}"

import os
from typing import List, Dict

from utils.vector_store import search_similar_chunks
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
GLOBAL_DOC_CONTEXT = "This is fallback content. No project documents were found."

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def list_user_project_files(project_name: str) -> List[str]:
    prefix = f"code_crew/{project_name}/"
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        return [item["Key"] for item in response.get("Contents", [])]
    except (BotoCoreError, ClientError) as e:
        print(f"⚠️ S3 list error: {e}")
        return []

def read_s3_file_content(key: str) -> str:
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return response["Body"].read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ S3 read error {key}: {e}")
        return ""

async def build_context(project_name: str, query: str) -> str:
    try:
        file_keys = list_user_project_files(project_name)

        if not file_keys:
            print(f"⚠️ No files found for project '{project_name}' in S3.")
            return GLOBAL_DOC_CONTEXT

        all_text = ""
        for key in file_keys:
            file_text = read_s3_file_content(key)
            all_text += f"\n{file_text}"

        if not all_text.strip():
            return GLOBAL_DOC_CONTEXT

        # Now pass full document text to vector store for similarity search
        similar_chunks: List[Dict] = search_similar_chunks(all_text, query)

        if not similar_chunks:
            return "(No relevant content found in vector store.)"

        chunk_texts = [chunk.get("text", "") for chunk in similar_chunks if "text" in chunk]
        context = "\n\n".join(chunk_texts)
        return context if context else "(No relevant content found.)"

    except Exception as e:
        print(f"Error in build_context: {str(e)}")
        return f"Failed to build context: {str(e)}"
