# FastAPI Backend

## Setup

### Requirements

Install [uv package and project manager](https://docs.astral.sh/uv/):

- For Linux and MacOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- For Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Local Development

1. Sync the backend dependencies with the environment:

```bash
cd backend
uv sync

cd ../frontend
npm install # Required to initialize Husky which manages the pre-commit hooks
```

- Activate the Python environment:
  ```bash
  source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
  ```

2. Set local environment variables:

- Create .env file from .env.example

- Fill in variable values:

```bash
OPENAI_API_KEY = <..key..>
```

3. Run a local PostgreSQL instace on Docker:

```bash
docker compose up db -d
```

4. Start the FastAPI development server:

```bash
uv run fastapi dev
```

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

### Docker Development

The backend service is containerized using Docker. You can run it using Docker Compose:

```bash
docker compose up backend
```

### Twilio Setup

Twilio is used for phone number verification by sending verification codes via SMS.

Unless this line is deleted, you have to set up your own account to try it out. Follow the links in .env.example to do so. Later we will make one general account for everyone to use.

#### Setup Instructions

1. Create a Twilio account at https://www.twilio.com/try-twilio
2. Get your credentials from the Twilio Console:
   - Account SID
   - Auth Token
   - Verify Service SID (create a new Verify Service if needed)
3. Add these to your `.env` file:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
   TEST_PHONE_NUMBER=your_phone_number  # E.164 format (e.g., +4915730709306)
   ```
4. Test the setup:
   ```bash
   python services/twilio_service.py
   ```

#### Important Notes

- Implementation will proceed once Next.js login functionality is ready
- The current `twilio_service.py` is for demonstration purposes only!
- This step is done BUT: To see how to setup twilio with supabase check https://supabase.com/docs/guides/auth/phone-login?showSmsProvider=Twilio#! . To set it in the CSEE x Personio Supabase account contact TA or META team

## Development Tools

- **uv**: For Python package management and virtual environments
- **Ruff**: For linting and code formatting
- **Pydantic**: For data validation
- **SQLAlchemy**: For database ORM
- **Alembic**: For database migrations
- **FastAPI**: For API development
- **Uvicorn**: For ASGI server
