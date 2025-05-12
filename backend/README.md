# FastAPI Backend

## Setup

### Requirements

Install [uv package and project manager](https://docs.astral.sh/uv/):

- For Linux and MacOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | less
```
- For Windows:
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
```


### Local Development

1. Sync the backend dependencies with the environment:
```bash
cd backend
uv sync
```
- (Optional) Activate the Python environment: 
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
├── config/
├── models/
├── routers/
├── schemas/
├── database.py
├── Dockerfile
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
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
