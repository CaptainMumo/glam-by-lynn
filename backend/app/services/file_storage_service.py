"""
File storage service
Handles file uploads to AWS S3 or local storage
"""
import os
import uuid
from typing import Optional, BinaryIO
from pathlib import Path
import mimetypes

from app.core.config import settings

# Try to import boto3 for S3 support
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False


class FileStorageService:
    """Service for handling file uploads to S3 or local storage"""

    def __init__(self):
        self.use_s3 = S3_AVAILABLE and bool(settings.S3_BUCKET_NAME and settings.AWS_ACCESS_KEY_ID)

        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            # Local storage fallback
            self.local_storage_path = Path("uploads")
            self.local_storage_path.mkdir(exist_ok=True)

    def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        folder: str = "products",
        content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to storage

        Args:
            file: File-like object to upload
            filename: Original filename
            folder: Folder/prefix to organize files
            content_type: MIME type of the file

        Returns:
            Public URL to access the file

        Raises:
            Exception: If upload fails
        """
        # Generate unique filename
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_key = f"{folder}/{unique_filename}"

        # Detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"

        if self.use_s3:
            return self._upload_to_s3(file, file_key, content_type)
        else:
            return self._upload_to_local(file, file_key)

    def _upload_to_s3(self, file: BinaryIO, file_key: str, content_type: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'
                }
            )

            # Return public URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            return url

        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {str(e)}")

    def _upload_to_local(self, file: BinaryIO, file_key: str) -> str:
        """Upload file to local storage"""
        file_path = self.local_storage_path / file_key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file.read())

        # Return local URL (relative path)
        # In production, this should be served by nginx or similar
        return f"/uploads/{file_key}"

    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage

        Args:
            file_url: URL or path to the file

        Returns:
            True if deleted successfully, False otherwise
        """
        if self.use_s3:
            return self._delete_from_s3(file_url)
        else:
            return self._delete_from_local(file_url)

    def _delete_from_s3(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            # Extract key from URL
            # Format: https://bucket.s3.region.amazonaws.com/folder/file.ext
            if file_url.startswith("https://"):
                parts = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")
                if len(parts) == 2:
                    file_key = parts[1]
                else:
                    return False
            else:
                file_key = file_url

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True

        except ClientError:
            return False

    def _delete_from_local(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract path from URL
            if file_url.startswith("/uploads/"):
                file_path = self.local_storage_path / file_url.replace("/uploads/", "")
            else:
                file_path = Path(file_url)

            if file_path.exists():
                file_path.unlink()
                return True
            return False

        except Exception:
            return False


# Global instance
file_storage = FileStorageService()
