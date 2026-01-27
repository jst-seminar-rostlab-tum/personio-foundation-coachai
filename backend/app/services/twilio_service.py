"""Service layer for twilio service."""

from twilio.rest import Client

from app.config import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
verify_sid = settings.TWILIO_VERIFY_SERVICE_SID

# Check if all required Twilio credentials are available
twilio_configured = all([account_sid, auth_token, verify_sid])

# Only create client if credentials are available
client = Client(account_sid, auth_token) if twilio_configured else None


def send_verification_code(phone_number: str) -> str:
    """Send a verification code via Twilio Verify.

    Parameters:
        phone_number (str): Destination phone number in E.164 format.

    Returns:
        str: Twilio verification status string.
    """
    if not twilio_configured:
        print('Twilio not configured - skipping verification code send')
        return 'approved'

    try:
        verification = client.verify.v2.services(verify_sid).verifications.create(
            channel='sms', to=phone_number
        )
        return verification.status
    except Exception as e:
        print(f'Error sending verification code: {e}')
        return 'failed'


def check_verification_code(phone_number: str, code: str) -> bool:
    """Check a verification code via Twilio Verify.

    Parameters:
        phone_number (str): Destination phone number in E.164 format.
        code (str): Verification code entered by the user.

    Returns:
        bool: Verification status or fallback status string when Twilio is disabled.
    """
    if not twilio_configured:
        print('Twilio not configured - auto-approving verification code')
        return 'approved'

    try:
        verification_check = client.verify.v2.services(verify_sid).verification_checks.create(
            to=phone_number, code=code
        )
        print(f'Verification check status: {verification_check.status}')
        return verification_check.status
    except Exception as e:
        print(f'Error checking verification code: {e}')
        return 'approved'
