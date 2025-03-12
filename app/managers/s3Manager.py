import os
from boto3 import session
from fastapi import HTTPException, UploadFile
from app.utils.singleton import Singleton

class S3Manager(metaclass=Singleton):
    """
    S3Manager handles S3 (MinIO) connections and file operations such as upload and delete.
    """

    def __init__(self):
        self.s3_client = self.__get_client()
        self.bucket_name = os.getenv('BUCKET_NAME')

    def __get_client(self):
        """
        Establishes a connection to the S3 (MinIO) client.
        """
        try:
            session_obj = session.Session()
            client = session_obj.client(
                's3',
                endpoint_url=os.getenv('ENDPOINT'),
                aws_access_key_id=os.getenv('ACCESS_KEY'),
                aws_secret_access_key=os.getenv('SECRET_KEY'),
                region_name="fra1",
            )
            
            return client
        except Exception as e:
            raise Exception(f"Failed to establish S3 client connection: {str(e)}")

    def upload_file(self, file: UploadFile, object_name: str = None, public: bool = False) -> str:
        """
        Uploads an UploadFile to the specified S3 bucket.

        :param file: UploadFile object from FastAPI
        :param object_name: S3 object name. If not specified, uses the file's filename.
        :param public: If True, sets the file's ACL to public-read.
        :return: URL of the uploaded file
        """
        if object_name is None:
            object_name = file.filename

        try:
            file.file.seek(0)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file.file,
                ContentType=file.content_type,
                ACL='public-read' if public else 'private'
            )
            url = f"{os.getenv('ENDPOINT')}/{self.bucket_name}/{object_name}"
            return url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to udez pload file: {str(e)}")

    def delete_file(self, object_name: str):
        """
        Deletes a file from the specified S3 bucket.

        :param object_name: S3 object name to delete
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    def get_file_url(self, object_name: str) -> str:
        """
        Generates the URL for a file stored in S3.

        :param object_name: S3 object name
        :return: URL string
        """
        return f"{os.getenv('ENDPOINT')}/{self.bucket_name}/{object_name}"