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
docker compose up supabase backend --build
```

### Option B: Console (better for developing)

Use this option when you’re doing active backend development, and need:

- Fast reloads
- Full control over logs and breakpoints
- Access to local Python environment / venv

**Steps:**

1. Install FFmpeg

   **For Windows:**

   a. Go to the official download page: https://ffmpeg.org/download.html

   b. Under “Get packages & executable files,” choose the Windows build.

   c. Download and unzip the archive (e.g. to `C:\ffmpeg`).

   d. Add FFmpeg to your PATH:

   - Open **System Properties** → **Advanced** → **Environment Variables**.
   - Under **System variables**, select **Path** → **Edit** → **New**, then enter `C:\ffmpeg\bin`.

   e. Restart your terminal/PowerShell and verify:

   ```powershell
   ffmpeg -version
   ```

   Steps also shown in this [YouTube video](https://www.youtube.com/watch?v=K7znsMo_48I).

   **For Mac:**

   ```
   # macOS (Homebrew)
   brew install ffmpeg

   # Debian / Ubuntu
   sudo apt update
   sudo apt install -y ffmpeg

   # Fedora / CentOS
   sudo dnf install -y ffmpeg

   # Verify installation
   ffmpeg -version
   ```

2. Sync the backend dependencies with the environment:

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

- Fill in variable values. GCP and Gemini on VertexAI use the same credentials, so make sure to set the env variables below to use LLM generative functions.

```bash
GCP_PRIVATE_KEY_ID=<...>
GCP_PRIVATE_KEY=<...>
GCP_CLIENT_EMAIL=<...>
GCP_CLIENT_ID=<...>
```

3. Run a local PostgreSQL instace:

```bash
cd supabase
npm install
npx supabase start
```
To stop it, run:
```bash
npx supabase stop
```

4. Populate local PostgreSQL with dummy data. From the backend folder, run the following:

```bash
uv run -m app.data.populate_dummy_data && uv run -m app.data.populate_static_data
```

5. Start the FastAPI development server:

```bash
uv run fastapi dev
```

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

### Hook Authentication Error
If you encounter any hook authentication errors when trying to log in or sign up locally, 
execute the following SQL query in your local Supabase instance:
```bash
CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Optionally inspect or modify the JWT claims here
  RETURN event;
END;
$$;
```

### Database Migrations with Alembic

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migration management. Alembic helps us track, version, and deploy database schema changes in a controlled and reproducible way, especially important for production deployments.

#### Overview

Alembic has been integrated with our backend models (`/backend/app/models`) and database configuration (`backend/app/database.py`). A pre-push hook automatically checks consistency between models and migration scripts, ensuring database integrity.

#### Development Workflow

##### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

##### 2. Start and initialize supabase

```bash
# Reset the local database
docker compose down supabase -v

# Start the database
docker compose up supabase -d

# Update db to latest schema
uv run alembic upgrade head
```

##### 3. Modify Models and Generate Migration

After making changes to your database models under `backend/app/models`:

```bash
# Generate migration script automatically
uv run alembic revision --autogenerate -m "descriptive message about your changes"
```

This creates a new migration file in the `backend/alembic/versions/` directory with the format:
`<timestamp>-<revision_id>_descriptive_message_about_your_changes.py`

##### 4. Review Generated Migration

**Important:** Always review the generated migration script before committing:

- Check the `upgrade()` function for correctness
- Verify the `downgrade()` function properly reverses changes
- Check imports and formatting
- If data needs to be inserted within the migration, add that to `backend/alembic/data`

##### 5. Test Migration Locally

```bash
# Apply the migration
uv run alembic upgrade head

# Test rollback functionality
uv run alembic downgrade -1

# Apply the migration again
uv run alembic upgrade head

# Verify model/migration consistency
uv run alembic check
```

##### 6. Update Dummy Data for Database

Update `backend/app/data/dummy_data` with your model changes. To see if everything works, populate the database with the dummy data:

```bash
docker compose up init-db -d
```

##### 7. Merge dev into your feature branch

If new migration scripts have been added to dev, you will encounter multiple alembic heads. Follow these steps:

```bash
# Check for multiple alembic heads. This should return two revision_id.
uv run alembic heads
```

- Update the `down_revision` in your migration script with the `revision_id` of the second alembic head coming from dev
- Make sure that your migration script and incoming script(s) from dev are compatible
- Repeat 5. and 6.

```bash
# Check for multiple alembic heads again. This should now only return the revision_id of your migration script.
uv run alembic heads
```

##### 8. Commit and Push your Changes

A pre-push hook is executed when committing changes to `backend/app/models`, `backend/alembic/versions` and/or `backend/alembic/data`. Within that hook the docker container `test-migrations` is run which executes `./husky/test-migrations.sh` against a separate database with the name `test_migrations`.

##### Important Rule

- **Never edit migration scripts once they're merged to `dev`**
- If changes are needed, create a follow-up migration instead

### Knowledge Database (Vector DB)

If you want to use the vector knowledge base, make sure you have a Gemini API Key and a Supabase URL in your `.env` file.
Run the following command to populate it:

```bash
uv run -m app.rag.populate_vector_db
```

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

## Development Tools

- **uv**: For Python package management and virtual environments
- **Ruff**: For linting and code formatting
- **Pydantic**: For data validation
- **SQLAlchemy**: For database ORM
- **Alembic**: For database migrations
- **FastAPI**: For API development
- **Uvicorn**: For ASGI server

## Structure

```
backend/
├─ app/
│  ├─ main.py            # FastAPI app entrypoint
│  ├─ config.py          # Settings and env var loading
│  ├─ connections/       # External clients (DB, caches, APIs)
│  ├─ data/              # Data loaders, dummy/static data scripts
│  ├─ dependencies/      # FastAPI dependency injection helpers
│  ├─ enums/             # Shared enum definitions
│  ├─ interfaces/        # Interfaces/abstractions for services
│  ├─ models/            # SQLAlchemy ORM models
│  ├─ rag/               # RAG workflow for LLM resources context
│  ├─ routers/           # API route handlers by domain
│  ├─ schemas/           # Pydantic request/response models (for API communication)
│  ├─ services/          # Business logic and domain services
│  └─ tests/             # Backend tests
├─ alembic/              # Migration tooling and scripts
│  ├─ versions/          # Auto-generated migration files
│  └─ data/              # Migration-related data helpers
├─ alembic.ini           # Alembic configuration
├─ pyproject.toml        # Python project metadata and dependencies
├─ uv.lock               # Locked dependency versions (uv)
├─ ruff.toml             # Ruff lint/format configuration
├─ Dockerfile            # Backend container build
├─ fly.toml              # Fly.io deployment config (prod)
├─ fly-dev.toml          # Fly.io deployment config (dev)
└─ README.md             # Backend documentation
```
