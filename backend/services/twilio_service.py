import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()  # THIS IS REQUIRED TO LOAD FROM .ENV

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
verify_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')

print(account_sid, auth_token, verify_sid)

client = Client(account_sid, auth_token)


def send_verification_code(phone_number):
    verification = client.verify.v2.services(verify_sid).verifications.create(
        to=phone_number,
        channel='sms',  # or 'call' for phone call
    )
    return verification.status


def check_verification_code(phone_number, code):
    verification_check = client.verify.v2.services(verify_sid).verification_checks.create(
        to=phone_number, code=code
    )
    return verification_check.status == 'approved'


# Send code
send_status = send_verification_code(os.getenv('TEST_PHONE_NUMBER'))
print('Send status:', send_status)

# Later, when user inputs the received code:
user_input_code = input('Enter the code you received: ')
is_verified = check_verification_code(os.getenv('TEST_PHONE_NUMBER'), user_input_code)

if is_verified:
    print('Phone number verified successfully!')
else:
    print('Verification failed.')
