import os

from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
# verify_service_sid = os.getenv('TWILIO_VERIFY_SERVICE_SID')

print(account_sid)
print(auth_token)

client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='+16812400988', body='this is a test message', to='+4915730709306'
)

print(message.sid)
