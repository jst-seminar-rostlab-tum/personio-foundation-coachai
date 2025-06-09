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

### Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migration management. Alembic helps us track, version, and deploy database schema changes in a controlled and reproducible way, especially important for production deployments.

#### Overview

Alembic has been integrated with our backend models (`/backend/app/models`) and database configuration (`backend/app/database.py`). A pre-commit hook automatically checks consistency between models and migration scripts, ensuring database integrity.

#### Development Workflow
##### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

##### 2. Start and initialize the local database
```bash
# Start the database
docker compose up db -d

# Initialize the database
uv run alembic upgrade head
```

##### 3. Modify Models and Generate Migration
After making changes to your database models under `backend/app/models`:

```bash
# Generate migration script automatically
uv run alembic revision --autogenerate -m "descriptive message about changes"
```

This creates a new migration file in the `backend/alembic/versions/` directory with the format:
`<timestamp>-<revision_id>_descriptive_message_about_changes.py`

##### 4. Review Generated Migration
**Important:** Always review the generated migration script before committing:

- Check the `upgrade()` function for correctness
- Verify the `downgrade()` function properly reverses changes
- Ensure data migration logic is included if needed

##### 5. Test Migration Locally

```bash
# Apply the migration
uv run alembic upgrade head

# Verify model/migration consistency
uv run alembic check

# Test rollback functionality
uv run alembic downgrade -1
```

##### 6. Update Dummy Data for Database
Update `backend/app/data/dummy_data` with your model changes. To see if everything works, populate the database with the dummy data:
```bash
docker compose up init-db -d
```

##### 6. Commit and Push
The pre-commit hook will automatically run `alembic check` to ensure consistency between models and migration scripts.

##### Important Rule
- **Never edit migration scripts once they're merged to `dev`**
- If changes are needed, create a follow-up migration instead

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
