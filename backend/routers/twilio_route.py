from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.twilio_service import send_verification_code, verify_code

router = APIRouter(prefix='/twilio', tags=['Twilio'])


class PhoneNumberRequest(BaseModel):
    phone_number: str


class VerificationRequest(BaseModel):
    phone_number: str
    code: str


@router.post('/send-verification')
async def send_verification(request: PhoneNumberRequest) -> dict[str, str]:
    try:
        await send_verification_code(request.phone_number)
        return {'message': 'Verification code sent successfully'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post('/check-verification')
async def check_verification(request: VerificationRequest) -> dict[str, bool]:
    try:
        is_valid = await verify_code(request.phone_number, request.code)
        return {'valid': is_valid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
