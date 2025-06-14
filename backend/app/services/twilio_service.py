from twilio.rest import Client

from app.config import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
verify_sid = settings.TWILIO_VERIFY_SERVICE_SID

if not all([account_sid, auth_token, verify_sid]):
    raise ValueError('Missing required Twilio credentials in .env file')

client = Client(account_sid, auth_token)


def send_verification_code(phone_number: str) -> str:
    verification = client.verify.v2.services(verify_sid).verifications.create(
        channel='sms', to=phone_number
    )

    return verification.status


def check_verification_code(phone_number: str, code: str) -> bool:
    verification_check = client.verify.v2.services(verify_sid).verification_checks.create(
        to=phone_number, code=code
    )

    print(f'Verification check status: {verification_check.status}')
    return verification_check.status
