import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import require_user
from app.services.google_cloud_storage_service import GCSManager

router = APIRouter(prefix='/signed-url', tags=['Signed URLs'], dependencies=[Depends(require_user)])
gcs_manager_docs = GCSManager('docs')
gcs_manager_audio = GCSManager('audio')


@router.get(
    '/docs',
    responses={
        200: {'description': 'Signed URL generated'},
        404: {'description': 'Document not found'},
        500: {'description': 'Internal server error'},
    },
)
def get_docs_signed_url(
    filename: str = Query(..., min_length=1, description='Name of the document file'),
) -> dict:
    try:
        url = gcs_manager_docs.generate_signed_url(filename)
    except FileNotFoundError as file_not_found_error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=(
                f"Document '{filename}' not found in bucket "
                f"'{gcs_manager_docs.bucket_name}/{gcs_manager_docs.prefix}'"
            ),
        ) from file_not_found_error
    except Exception as exception:
        logging.exception('Error generating signed URL for docs')
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Could not generate signed URL for document. Please try again later.',
        ) from exception
    return {'url': url}


@router.get(
    '/audio',
    responses={
        200: {'description': 'Signed URL generated'},
        404: {'description': 'Audio file not found'},
        500: {'description': 'Internal server error'},
    },
)
def get_audio_signed_url(
    filename: str = Query(..., min_length=1, description='Name of the audio file'),
) -> dict:
    try:
        url = gcs_manager_audio.generate_signed_url(filename)
    except FileNotFoundError as file_not_found_error:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=(
                f"Audio file '{filename}' not found in bucket "
                f"'{gcs_manager_audio.bucket_name}/{gcs_manager_audio.prefix}'"
            ),
        ) from file_not_found_error
    except Exception as exception:
        logging.exception('Error generating signed URL for audio')
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Could not generate signed URL for audio. Please try again later.',
        ) from exception
    return {'url': url}
