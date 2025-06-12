import logging
import os

from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
sender_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
twilio_service = os.getenv('TWILIO_SERVICE_SID')

if not all([account_sid, auth_token, sender_phone_number]):
    raise ValueError('Missing required Twilio environment variables. Please check your .env file.')

client = Client(account_sid, auth_token)
logger = logging.getLogger(__name__)


async def send_verification_code(phone_number: str) -> str:
    """
    Send a verification code to the specified phone number using Twilio SMS.
    """
    verification = client.verify.v2.services(twilio_service).verifications.create(
        channel='sms', to=phone_number
    )

    print(verification.status)
    if verification.status == 'pending':
        print("Verification code sent to the user's phone number.")
    else:
        print('Verification code could not be sent.')

    # logger.info(f'Message sent to {phone_number}: {message.sid}')
    return verification.sid


async def verify_code(phone_number: str, code: str) -> bool:
    verification_check = client.verify.v2.services(twilio_service).verification_checks.create(
        to=phone_number, code=code
    )

    print(verification_check.status)
    if verification_check.status == 'approved':
        print('Verification code is valid.')
        return True
    else:
        print('Verification code is not valid.')
        return False


# Store verification codes temporarily (phone_number -> code)
# verification_codes: dict[str, str] = {}


# generate a random 6 digits code for the user to enter based on the current time
# def generate_code() -> str:
#     code = str(int(round(time.time() * 1000) % 1000000))
#     return code.zfill(6)


# async def send_verification_code(phone_number: str) -> str:
#     """
#     Send a verification code to the specified phone number using Twilio SMS.
#     """
#     code = generate_code()
#     verification_codes[phone_number] = code

#     message = client.messages.create(
#         from_=sender_phone_number,
#         body=f'Welcome to CoachAI. Your verification code is {code}',
#         to=phone_number,
#     )
#     logger.info(f'Message sent to {phone_number}: {message.sid}')
#     return message.sid


# async def verify_code(phone_number: str, code: str) -> bool:
#     """
#     Verify the code sent to the phone number.
#     """
#     print('code', code)
#     print(verification_codes)
#     stored_code = verification_codes.get(phone_number)
#     if not stored_code:
#         logger.error(f'No verification code found for {phone_number}')
#         return False

#     is_valid = stored_code == code
#     if is_valid:
#         # Remove the code after successful verification
#         del verification_codes[phone_number]
#     print(is_valid)

#     print(stored_code)
#     return is_valid
