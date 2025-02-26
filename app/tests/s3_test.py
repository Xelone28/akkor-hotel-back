import pytest
import boto3
import botocore.exceptions
from moto import mock_aws
from app.managers.s3Manager import S3Manager

def ensure_bucket_exists(s3_client, bucket_name):
    """Checks if the bucket exists. If not, create it."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)  # Check existence
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:  # Bucket does not exist
            s3_client.create_bucket(Bucket=bucket_name)

@pytest.fixture
def fake_s3():
    """Mocks MinIO storage and ensures a clean bucket."""
    with mock_aws():
        s3 = boto3.client(
            's3',
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )
        ensure_bucket_exists(s3, "testbucket")  # Avoid 'AlreadyOwned' error
        yield s3

@pytest.mark.asyncio
async def test_s3_upload(fake_s3):
    """Tests if file uploads correctly to MinIO."""
    s3_manager = S3Manager()
    s3_manager.bucket_name = "testbucket"

    file_path = "/tmp/test_file.txt"
    with open(file_path, "w") as f:
        f.write("Hello MinIO!")

    s3_manager.upload_file(file_path, "test_file.txt")

    objects = fake_s3.list_objects_v2(Bucket="testbucket")
    assert any(obj['Key'] == "test_file.txt" for obj in objects.get("Contents", []))