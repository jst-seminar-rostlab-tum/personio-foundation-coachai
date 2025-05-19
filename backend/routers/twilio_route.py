from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr

from ..services.twilio_service import twilio_service

router = APIRouter(prefix='/twilio', tags=['Twilio'])


class SMSRequest(BaseModel):
    to_number: constr(regex=r'^\+[1-9]\d{1,14}$')  # E.164 format
    message: str


@router.post('/sms')
async def send_sms(request: SMSRequest):
    """
    Send an SMS message using Twilio.
    """
    result = await twilio_service.send_sms(request.to_number, request.message)
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])
    return result
