from app.config import Settings
from app.services.google_cloud_storage_service import GCSManager

settings = Settings()

_gcs_audio_manager: GCSManager = None
_gcs_docs_manager: GCSManager = None


def _is_authorized_for_gcs() -> bool:
    return all(
        [
            settings.GCP_PRIVATE_KEY_ID,
            settings.GCP_PRIVATE_KEY,
            settings.GCP_CLIENT_EMAIL,
            settings.GCP_CLIENT_ID,
        ]
    )


def get_gcs_audio_manager() -> GCSManager:
    global _gcs_audio_manager
    if _gcs_audio_manager:
        return _gcs_audio_manager
    elif _is_authorized_for_gcs():
        _gcs_audio_manager = GCSManager('audio')
        return _gcs_audio_manager
    return None


def get_gcs_docs_manager() -> GCSManager:
    global _gcs_docs_manager
    if _gcs_docs_manager:
        return _gcs_docs_manager
    elif _is_authorized_for_gcs():
        _gcs_docs_manager = GCSManager('docs')
        return _gcs_docs_manager
    return None
