import os
import time

import jwt
from dotenv import load_dotenv

if not load_dotenv():
    print('⚠️  .env file not found or failed to load.')
    exit(1)

secret = os.getenv('SUPABASE_JWT_SECRET')

if not secret or len(secret) < 32:
    print('❌ SUPABASE_JWT_SECRET is missing or too short (must be at least 32 characters).')
    exit(1)

now = int(time.time())

payload = {
    'role': 'anon',
    'aud': 'authenticated',
    'iss': 'supabase',
    'sub': 'user_id',
    'iat': now,
    'exp': now + 60 * 60 * 24 * 90,  # 90 days (for local development)
}

token = jwt.encode(payload, secret, algorithm='HS256')

# `jwt.encode()` returns bytes in PyJWT < 2.0, string in >= 2.0
if isinstance(token, bytes):
    token = token.decode('utf-8')

print(token)
