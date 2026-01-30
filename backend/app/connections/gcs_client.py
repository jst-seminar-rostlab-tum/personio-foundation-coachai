"""External service clients for gcs client."""

from app.config import Settings
from app.services.google_cloud_storage_service import GCSManager

settings = Settings()

_gcs_audio_manager: GCSManager = None
_gcs_docs_manager: GCSManager = None


def _is_authorized_for_gcs() -> bool:
    """Check whether GCP credentials are configured for GCS usage.

    Returns:
        bool: True when all required GCP credential settings are present.
    """
    return all(
        [
            settings.GCP_PRIVATE_KEY_ID,
            settings.GCP_PRIVATE_KEY,
            settings.GCP_CLIENT_EMAIL,
            settings.GCP_CLIENT_ID,
        ]
    )


def get_gcs_audio_manager() -> GCSManager:
    """Return a cached GCS manager for audio assets.

    Returns:
        GCSManager: Manager for the audio bucket, or None if not authorized.
    """
    global _gcs_audio_manager
    if _gcs_audio_manager:
        return _gcs_audio_manager
    elif _is_authorized_for_gcs():
        _gcs_audio_manager = GCSManager('audio')
        return _gcs_audio_manager
    return None


def get_gcs_docs_manager() -> GCSManager:
    """Return a cached GCS manager for document assets.

    Returns:
        GCSManager: Manager for the docs bucket, or None if not authorized.
    """
    global _gcs_docs_manager
    if _gcs_docs_manager:
        return _gcs_docs_manager
    elif _is_authorized_for_gcs():
        _gcs_docs_manager = GCSManager('docs')
        return _gcs_docs_manager
    return None
