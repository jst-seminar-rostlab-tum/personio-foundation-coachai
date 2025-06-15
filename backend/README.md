# CoachAI Backend

## Requirements

Install [uv package and project manager](https://docs.astral.sh/uv/):

- For Linux and MacOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- For Windows:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

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
You can skip these steps below if you don't want to use phone number verification, the default is to auto-approve any verification code.

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
   ```


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
