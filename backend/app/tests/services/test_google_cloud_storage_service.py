from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from app.services.google_cloud_storage_service import GCSManager


@pytest.fixture
def gcs_manager() -> GCSManager:
    with (
        patch('app.services.google_cloud_storage_service.settings') as mock_settings,
        patch('app.services.google_cloud_storage_service.storage.Client'),
        patch(
            'app.services.google_cloud_storage_service.service_account.Credentials.from_service_account_info'
        ) as mock_creds,
    ):
        mock_settings.GCP_PROJECT_ID = 'dummy'
        mock_settings.GCP_PRIVATE_KEY_ID = 'dummy'
        mock_settings.GCP_PRIVATE_KEY = (
            '-----BEGIN PRIVATE KEY-----\\ndummy\\n-----END PRIVATE KEY-----\\n'
        )
        mock_settings.GCP_CLIENT_EMAIL = 'dummy@dummy.iam.gserviceaccount.com'
        mock_settings.GCP_CLIENT_ID = 'dummy'
        mock_settings.GCP_BUCKET = 'dummy'
        mock_creds.return_value = MagicMock()
        manager = GCSManager('audio')
        manager.bucket = MagicMock()
        return manager


def test_delete_document_exists(gcs_manager: GCSManager) -> None:
    blob = MagicMock()
    blob.exists.return_value = True
    gcs_manager.bucket.blob.return_value = blob

    gcs_manager.delete_document('testfile.mp3')
    blob.delete.assert_called_once()


def test_delete_document_not_exists(gcs_manager: GCSManager, caplog: LogCaptureFixture) -> None:
    blob = MagicMock()
    blob.exists.return_value = False
    gcs_manager.bucket.blob.return_value = blob

    gcs_manager.delete_document('nofile.mp3')
    blob.delete.assert_not_called()
    assert any('Blob does not exist' in record.message for record in caplog.records)


def test_document_exists_true(gcs_manager: GCSManager) -> None:
    blob = MagicMock()
    blob.exists.return_value = True
    gcs_manager.bucket.blob.return_value = blob
    assert gcs_manager.document_exists('file.mp3') is True


def test_document_exists_false(gcs_manager: GCSManager) -> None:
    blob = MagicMock()
    blob.exists.return_value = False
    gcs_manager.bucket.blob.return_value = blob
    assert gcs_manager.document_exists('file.mp3') is False
