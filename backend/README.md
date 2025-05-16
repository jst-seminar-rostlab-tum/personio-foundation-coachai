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
```

- Activate the Python environment:
  ```bash
  source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
  ```

2. Start the PostgreSQL database:

```bash
docker compose up db -d
```

3. Run the development server:

```bash
uv run fastapi dev
```

### Docker Development

The backend service is containerized using Docker. You can run it using Docker Compose:

```bash
docker compose up backend
```

## Project Structure

```
backend/
├── models/
├── routers/
├── schemas/
├── database.py
├── Dockerfile
├── .env.example
├── .env  # Needs to be created by copying .env.example and configuring it
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Development Tools

- **uv**: For Python package management and virtual environments
- **Ruff**: For linting and code formatting
- **Pydantic**: For data validation
- **SQLAlchemy**: For database ORM
- **Alembic**: For database migrations
- **FastAPI**: For API development
- **Uvicorn**: For ASGI server
