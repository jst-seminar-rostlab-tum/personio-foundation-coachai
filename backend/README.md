# FastAPI Backend

## Setup

### Local Development (this is already implemented in Dockerfile)

1. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
```

2. Install dependencies:
```bash
uv pip install .
```

3. Run the development server:
```bash
python -m uvicorn backend.main:app --reload
```

### Docker Development

The backend service is containerized using Docker. You can run it using Docker Compose:

```bash
docker compose up backend
```

## Project Structure

```
backend/
├── src/
│   └── backend/
│       ├── api/
│       ├── config/
│       ├── models/
│       ├── schemas/
│       ├── main.py
│       ├── database.py
│       └── scripts.py
├── pyproject.toml
└── Dockerfile
```

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## API Endpoints

### Messages

- `GET /messages/`
  - List all messages
  - Query parameters:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)

- `POST /messages/`
  - Create a new message
  - Request body:
    ```json
    {
      "content": "string"
    }
    ```

## Development Tools

- **uv**: For Python package management and virtual environments
- **Ruff**: For linting and code formatting
- **Black**: For code formatting
- **Pydantic**: For data validation
- **SQLAlchemy**: For database ORM
- **Alembic**: For database migrations
- **FastAPI**: For API development
- **Uvicorn**: For ASGI server
- **Docker**: For containerization
