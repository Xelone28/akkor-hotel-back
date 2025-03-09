import boto3
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_BUCKET = os.getenv("MINIO_BUCKET", "hotel-pictures")
S3_CDN_URL = os.getenv("S3_CDN_URL", f"{S3_ENDPOINT}/{S3_BUCKET}")  # Auto CDN URL

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

    def upload_file(self, file_path: str):
        """Uploads a file and returns its public CDN URL."""
        file_uuid = str(uuid.uuid4())
        self.s3_client.upload_file(file_path, self.bucket_name, file_uuid)
        return f"{S3_CDN_URL}/{file_uuid}"   # ✅ Generates Full Public CDN URL

    def get_file_url(self, object_uuid: str):
        """Returns the public URL of a file in S3 bucket."""
        return f"{S3_CDN_URL}/{object_uuid}"   # ✅ Directly fetches the public URL