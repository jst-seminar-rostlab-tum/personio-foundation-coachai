from pathlib import Path

from app.services.google_cloud_storage_service import GCSManager

if __name__ == '__main__':
    local_docs_path = Path(__file__).parents[1] / 'rag' / 'documents'
    local_downloads_path = Path(__file__).parents[1] / 'rag' / 'downloads'
    manager = GCSManager(folder='docs')
    manager.upload_documents(directory=local_docs_path)
    manager.download_documents(directory=local_downloads_path)
    documents = manager.list_documents()
    print('Remote GCS documents:')
    for doc in documents:
        print('-', doc)
