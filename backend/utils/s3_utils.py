import boto3
import os
from botocore.exceptions import NoCredentialsError

BUCKET_NAME = "obscene-files-bucket"
s3 = boto3.client("s3")

def upload_to_s3(file_path: str, s3_key: str) -> bool:
    try:
        s3.upload_file(file_path, BUCKET_NAME, s3_key)
        return True
    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        return False
    except Exception as e:
        print("❌ S3 Upload error:", e)
        return False

def check_project_exists_in_s3(folder_prefix: str) -> bool:
    try:
        result = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_prefix + "/")
        return 'Contents' in result
    except Exception as e:
        print("❌ Error checking S3 folder:", e)
        return False
