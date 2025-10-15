import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from typing import Optional, BinaryIO
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """Handle file uploads/downloads to S3/Cloudflare R2."""

    def __init__(self):
        # Configure boto3 client with proper signature version
        boto_config = Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'}  # Use virtual-hosted-style for AWS S3
        )

        # Prepare client arguments
        client_kwargs = {
            'service_name': 's3',
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY,
            'region_name': settings.S3_REGION,
            'config': boto_config
        }

        # Only add endpoint_url for non-AWS S3 (like Cloudflare R2)
        # For AWS S3, boto3 will automatically use the correct regional endpoint
        if settings.S3_ENDPOINT_URL and 'amazonaws.com' not in settings.S3_ENDPOINT_URL:
            client_kwargs['endpoint_url'] = settings.S3_ENDPOINT_URL
            # Use path-style for custom endpoints
            boto_config = Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'}
            )
            client_kwargs['config'] = boto_config

        self.s3_client = boto3.client(**client_kwargs)
        self.bucket = settings.S3_BUCKET

        logger.info(f"Initialized S3 client for bucket '{self.bucket}' in region '{settings.S3_REGION}'")

    def upload_file(
        self,
        file_path: str,
        object_name: str,
        content_type: Optional[str] = None
    ) -> bool:
        """Upload a file to S3/R2."""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_file(
                file_path,
                self.bucket,
                object_name,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded {file_path} to {object_name}")
            return True
        except ClientError as e:
            error_msg = f"Upload failed for {file_path}: {e}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        object_name: str,
        content_type: Optional[str] = None
    ) -> bool:
        """Upload file object to S3/R2."""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                object_name,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded file object to {object_name}")
            return True
        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            return False

    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download a file from S3/R2."""
        try:
            self.s3_client.download_file(
                self.bucket,
                object_name,
                file_path
            )
            logger.info(f"Downloaded {object_name} to {file_path}")
            return True
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            return False

    def get_presigned_url(
        self,
        object_name: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """Generate a presigned URL for object access."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def delete_file(self, object_name: str) -> bool:
        """Delete a file from S3/R2."""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=object_name
            )
            logger.info(f"Deleted {object_name}")
            return True
        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> list:
        """List files in S3/R2 with given prefix."""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            logger.error(f"List failed: {e}")
            return []

    def get_file_size(self, object_name: str) -> Optional[int]:
        """Get file size in bytes."""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket,
                Key=object_name
            )
            return response['ContentLength']
        except ClientError as e:
            logger.error(f"Failed to get file size: {e}")
            return None

# Global instance
storage_service = StorageService()
