# CoachAI Backend

## Requirements

#### Set up uv package manager

Install [uv package and project manager](https://docs.astral.sh/uv/):

- For Linux and MacOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- For Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Set up Supabase
Copy all Supabase `.env.example` variables into your `.env` file.
The `SUPABASE_ANON_KEY` must be signed with JWT. For this, run: 
```bash
uv run -m backend.app.rag.anon_key_jwt_generator
```
and put the resulting code as `SUPABASE_ANON_KEY`.

**Option B: Create a Free Account**

1. Create a supabse account (free tier) on [Supabase](https://supabase.com/dashboard/sign-in) and sign in.
2. Create a new Project and copy your Password into the .env file under `SUPABASE_PASSWORD`
3. Go to your Project -> Project Settings -> General
4. Copy your `Project Id` into the .env file as `SUPABASE_PROJECT_ID`
5. Go to API keys
6. Copy your `anon public key` into the .env file as `SUPABASE_KEY`
7. (optional but recommended): Go to Database, download the ssl certificate, and put it into the /backend/certs directory.
8. Copy the other settings from the .env.example into the .env file

## Local Development

### Option A: Docker (easier)

Use this option if you want to run the backend quickly without setting up a local Python environment. This is the easiest way to get started — especially useful for frontend developers who just need the API running.

```bash
docker compose up db backend --build
```

### Option B: Console (better for developing)

Use this option when you’re doing active backend development, and need:

- Fast reloads
- Full control over logs and breakpoints
- Access to local Python environment / venv

**Steps:**

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

- Fill in variable values. Reach out to TA or Ron for keys.

```bash
OPENAI_API_KEY = <..key..>
```

3. Run a local PostgreSQL instace on Docker:

```bash
docker compose up db -d
```

4. Populate local PostgreSQL with dummy data. From the backend folder, run the following:

```bash
uv run -m app.data.populate_dummy_data
```

5. Start the FastAPI development server:

```bash
uv run fastapi dev
```

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

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

## Updating PostgreSQL Password (Local Docker)

If the PostgreSQL password has changed and you need to apply the new password locally, follow these steps:

1. Stop and remove the existing containers and volume:

```bash
docker-compose down -v
```

The -v flag ensures the associated volume (which stores PostgreSQL data) is deleted. This is necessary to avoid authentication errors due to the old password.

2. Run a local PostgreSQL instace on Docker:

```bash
docker compose up db -d
```

## Development Tools

- **uv**: For Python package management and virtual environments
- **Ruff**: For linting and code formatting
- **Pydantic**: For data validation
- **SQLAlchemy**: For database ORM
- **Alembic**: For database migrations
- **FastAPI**: For API development
- **Uvicorn**: For ASGI server
