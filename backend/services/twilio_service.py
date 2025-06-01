import logging
import os

from dotenv import load_dotenv

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
verify_service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')

# Comment out actual Twilio client initialization for testing
# client = Client(account_sid, auth_token)

# Comment out actual SMS sending for testing
# message = client.messages.create(
#     from_='+16812400988',
#     body='this is a test message',
#     to='+4915730709306'
# )
# print(message.sid)

# Hardcoded verification code for testing
TEST_VERIFICATION_CODE = '123456'

logger = logging.getLogger(__name__)


async def send_verification_code(phone_number: str) -> str:
    """
    Send a verification code to the specified phone number.
    In test mode, just prints the code instead of sending it.
    """
    try:
        # For testing: just print the code and return success
        print(
            f'TEST MODE: Verification code {TEST_VERIFICATION_CODE} would be sent to {phone_number}'
        )
        return 'pending'
    except Exception as e:
        raise Exception(f'Failed to send verification code: {str(e)}') from e


async def verify_code(phone_number: str, code: str) -> bool:
    """
    Verify the code sent to the phone number.
    In test mode, checks against the test code.
    """
    try:
        # For testing: just check against the test code
        return code == TEST_VERIFICATION_CODE
    except Exception as e:
        raise Exception(f'Failed to verify code: {str(e)}') from e
