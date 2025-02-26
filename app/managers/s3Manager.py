import boto3
import os
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

if not all([S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET]):
    raise ValueError("S3 configuration variables are missing")

class S3Manager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(S3Manager, cls).__new__(cls)

            cls._instance.s3_client = boto3.client(
                's3',
                endpoint_url=S3_ENDPOINT,
                aws_access_key_id=S3_ACCESS_KEY,
                aws_secret_access_key=S3_SECRET_KEY,
            )
            
            cls._instance.bucket_name = S3_BUCKET

        return cls._instance

    def upload_file(self, file_path: str, object_name: str):
        self.s3_client.upload_file(file_path, self.bucket_name, object_name)
        return f"File {object_name} uploaded successfully"

    def download_file(self, object_name: str, output_path: str):
        self.s3_client.download_file(self.bucket_name, object_name, output_path)
        return f"File {object_name} downloaded successfully to {output_path}"

    def list_files(self):
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        return [item["Key"] for item in response.get("Contents", [])]