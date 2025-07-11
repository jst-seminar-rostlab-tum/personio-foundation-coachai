from unittest.mock import MagicMock, patch

import pytest
from pytest import LogCaptureFixture

from app.services.google_cloud_storage_service import GCSManager


@pytest.fixture
def gcs_manager() -> GCSManager:
    with patch('app.services.google_cloud_storage_service.storage.Client'):
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
