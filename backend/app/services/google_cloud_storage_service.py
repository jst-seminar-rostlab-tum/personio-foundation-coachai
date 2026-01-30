"""Service layer for google cloud storage service."""

import logging
from datetime import timedelta
from pathlib import Path
from typing import BinaryIO, Literal

from google.cloud import storage
from google.oauth2 import service_account

from app.config import settings


class GCSManager:
    """Manage uploads and downloads to Google Cloud Storage."""

    GCSFolderType = Literal['docs', 'audio']

    def __init__(self, folder: GCSFolderType) -> None:
        """Initialize a GCS manager scoped to a folder prefix.

        Parameters:
            folder (GCSFolderType): Folder prefix to scope operations to.
        """
        creds_info = {
            'type': 'service_account',
            'project_id': settings.GCP_PROJECT_ID,
            'private_key_id': settings.GCP_PRIVATE_KEY_ID,
            'private_key': settings.GCP_PRIVATE_KEY.replace('\\n', '\n'),
            'client_email': settings.GCP_CLIENT_EMAIL,
            'client_id': settings.GCP_CLIENT_ID,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': f'https://www.googleapis.com/robot/v1/metadata/x509/{settings.GCP_CLIENT_EMAIL}',
            'universe_domain': 'googleapis.com',
        }
        credentials = service_account.Credentials.from_service_account_info(creds_info)

        self.bucket_name: str = settings.GCP_BUCKET
        self.prefix: str = f'{folder}/'
        base_dir = Path(__file__).resolve().parent.parent / 'rag'
        self.local_dir = base_dir / 'documents'
        self.download_dir = base_dir / 'downloaded_docs'

        self.client = storage.Client(credentials=credentials, project=creds_info['project_id'])
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_documents(self, directory: Path | None = None) -> None:
        """Upload documents from a local directory into GCS.

        Parameters:
            directory (Path | None): Directory to upload from, defaults to local docs dir.

        Returns:
            None: This function uploads files to GCS.
        """
        upload_dir = Path(directory) if directory else self.local_dir

        if not upload_dir.exists() or not upload_dir.is_dir():
            raise ValueError(f'Invalid directory: {upload_dir}')

        for path in upload_dir.iterdir():
            if not path.is_file():
                continue
            blob_name = f'{self.prefix}{path.name}'
            blob = self.bucket.blob(blob_name)
            if blob.exists(self.client):
                print(f'Skipped (already exists): {blob_name}')
                continue
            blob.upload_from_filename(path)
            print(f'{path.name} → gs://{self.bucket.name}/{blob_name}')

    def upload_from_fileobj(
        self, file_obj: BinaryIO, blob_name: str, content_type: str | None = None
    ) -> str:
        """Upload a file-like object to GCS.

        Parameters:
            file_obj (BinaryIO): File-like object to upload.
            blob_name (str): Destination blob name.
            content_type (str | None): Optional content type to set.

        Returns:
            str: GCS URI of the uploaded object.
        """
        blob = self.bucket.blob(f'{self.prefix}{blob_name}')

        file_obj.seek(0)  # rewind to beginning
        blob.upload_from_file(file_obj, content_type=content_type)

        print(f'{blob_name} → gs://{self.bucket.name}/{blob.name}')
        return f'gs://{self.bucket.name}/{blob.name}'

    def download_documents(self, directory: Path | None = None) -> None:
        """Download all documents under the prefix to a local directory.

        Parameters:
            directory (Path | None): Destination directory for downloads.

        Returns:
            None: This function downloads files to disk.
        """
        target_dir = Path(directory) if directory else self.download_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        blobs = self.client.list_blobs(self.bucket, prefix=self.prefix)
        for blob in blobs:
            if blob.name.endswith('/'):
                continue
            local_path = target_dir / Path(blob.name).name
            blob.download_to_filename(local_path)
            print(f'Downloaded {blob.name} → {local_path}')

    def delete_all_documents(self) -> None:
        """Delete all documents under the current prefix.

        Returns:
            None: This function deletes blobs in the bucket.
        """
        blobs = self.client.list_blobs(self.bucket, prefix=self.prefix)
        deleted = 0
        for blob in blobs:
            if blob.name.endswith('/'):
                continue
            blob.delete()
            print(f'Deleted {blob.name}')
            deleted += 1
        print(f'Total deleted: {deleted}')

    def list_documents(self) -> list[str]:
        """List documents under the current prefix.

        Returns:
            list[str]: Blob names under the prefix.
        """
        blobs = self.client.list_blobs(self.bucket, prefix=self.prefix)
        return [blob.name for blob in blobs if not blob.name.endswith('/')]

    def generate_signed_url(self, filename: str, expiration_minutes: int = 5) -> str:
        """Generate a signed download URL for a blob.

        Parameters:
            filename (str): Blob filename relative to the prefix.
            expiration_minutes (int): URL validity period in minutes.

        Returns:
            str: Signed URL string.

        Raises:
            FileNotFoundError: If the blob does not exist.
        """
        blob_name = f'{self.prefix}{filename}'
        blob = self.bucket.blob(blob_name)

        if not blob.exists(self.client):
            raise FileNotFoundError(f'Blob does not exist: {blob_name}')

        return blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=expiration_minutes),
            method='GET',
        )

    def document_exists(self, filename: str) -> bool:
        """Check if a document exists in the GCS bucket under the current prefix.

        Parameters:
            filename (str): Blob filename relative to the prefix.

        Returns:
            bool: True if the blob exists.
        """
        blob_name = f'{self.prefix}{filename}'
        blob = self.bucket.blob(blob_name)
        return blob.exists(self.client)

    def delete_document(self, filename: str) -> None:
        """Delete a single document (blob) from GCS under the current prefix.

        Parameters:
            filename (str): Blob filename relative to the prefix.

        Returns:
            None: This function deletes a blob if it exists.
        """
        blob_name = f'{self.prefix}{filename}'
        blob = self.bucket.blob(blob_name)
        if blob.exists(self.client):
            blob.delete()
        else:
            logging.warning(f'Blob does not exist: {blob_name}')

    def download_to_bytesio(self, filename: str) -> BinaryIO:
        """Download a single file into a BytesIO object.

        Parameters:
            filename (str): Blob filename relative to the prefix.

        Returns:
            BinaryIO: In-memory bytes buffer with the file content.

        Raises:
            FileNotFoundError: If the blob does not exist.
        """
        import io

        blob_name = f'{self.prefix}{filename}'
        blob = self.bucket.blob(blob_name)

        if not blob.exists(self.client):
            raise FileNotFoundError(f'Blob does not exist: {blob_name}')

        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)
        return buffer
