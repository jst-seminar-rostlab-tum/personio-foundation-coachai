import os
from datetime import timedelta
from pathlib import Path
from typing import Literal

from google.cloud import storage
from google.oauth2 import service_account

from app.config import settings


class GCSManager:
    GCSFolderType = Literal['docs', 'audio']

    def __init__(self, folder: GCSFolderType) -> None:
        creds_info = {
            'type': 'service_account',
            'project_id': settings.GCP_PROJECT_ID,
            'private_key_id': settings.GCP_PRIVATE_KEY_ID,
            'private_key': settings.GCP_PRIVATE_KEY,
            'client_email': settings.GCP_CLIENT_EMAIL,
            'client_id': settings.GCP_CLIENT_ID,
            'auth_uri': settings.GCP_AUTH_URI,
            'token_uri': settings.GCP_TOKEN_URI,
            'auth_provider_x509_cert_url': settings.GCP_AUTH_PROVIDER_CERT_URL,
            'client_x509_cert_url': settings.GCP_CLIENT_CERT_URL,
            'universe_domain': settings.GCP_UNIVERSE_DOMAIN,
        }

        credentials = service_account.Credentials.from_service_account_info(creds_info)

        self.bucket_name: str = os.getenv('GCP_BUCKET', 'coachai')
        self.prefix: str = f'{folder}/'
        base_dir = Path(__file__).resolve().parent.parent / 'rag'
        self.local_dir = base_dir / 'documents'
        self.download_dir = base_dir / 'downloaded_docs'

        self.client = storage.Client(credentials=credentials, project=creds_info['project_id'])
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_documents(self, directory: Path = None) -> None:
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

    def download_documents(self, directory: Path = None) -> None:
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
        blobs = self.client.list_blobs(self.bucket, prefix=self.prefix)
        return [blob.name for blob in blobs if not blob.name.endswith('/')]

    def generate_signed_url(self, filename: str, expiration_minutes: int = 5) -> str:
        blob_name = f'{self.prefix}{filename}'
        blob = self.bucket.blob(blob_name)

        if not blob.exists(self.client):
            raise FileNotFoundError(f'Blob does not exist: {blob_name}')

        return blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=expiration_minutes),
            method='GET',
        )
