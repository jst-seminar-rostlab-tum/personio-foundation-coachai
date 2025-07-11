import os

from app.services.google_cloud_storage_service import GCSManager


def test_gcs_integration() -> None:
    """
    集成测试：需要设置 GOOGLE_APPLICATION_CREDENTIALS 或 settings 里所有 GCP 字段。
    真实连接 GCS，上传、检查、删除一个测试文件。
    """
    manager = GCSManager('audio')
    test_filename = 'testfile_gcs_integration.txt'
    # 创建本地测试文件
    with open(test_filename, 'w') as f:
        f.write('hello gcs integration test')
    # 上传到 GCS
    blob = manager.bucket.blob(f'{manager.prefix}{test_filename}')
    blob.upload_from_filename(test_filename)
    print(f'Uploaded {test_filename} to GCS')
    # 检查文件是否存在
    exists = manager.document_exists(test_filename)
    print(f'File exists in GCS: {exists}')
    assert exists, 'File should exist in GCS after upload'
    # 删除文件
    manager.delete_document(test_filename)
    print(f'Deleted {test_filename} from GCS')
    # 检查文件是否已删除
    exists_after = manager.document_exists(test_filename)
    print(f'File exists after delete: {exists_after}')
    assert not exists_after, 'File should not exist in GCS after deletion'
    # 清理本地文件
    os.remove(test_filename)
