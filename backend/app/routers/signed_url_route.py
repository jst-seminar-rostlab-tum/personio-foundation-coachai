from fastapi import APIRouter

from app.services.google_cloud_storage_service import GCSManager

router = APIRouter(prefix='/signed-url', tags=['Signed URLs'])


@router.get('/docs')
def get_docs_signed_url(filename: str) -> dict:
    gcs = GCSManager('docs')
    return {'url': gcs.generate_signed_url(filename)}


@router.get('/audio')
def get_audio_signed_url(filename: str) -> dict:
    gcs = GCSManager('audio')
    return {'url': gcs.generate_signed_url(filename)}
