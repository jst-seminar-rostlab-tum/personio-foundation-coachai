# Next.js + FastAPI Message Board

A simple full-stack application built with Next.js, FastAPI, and PostgreSQL.


### Frontend
- Next.js 15.3.2
- TypeScript
- TailwindCSS
- SWR for data fetching

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Start the application using Docker Compose:
```bash
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

Find our dev guidelines [here](https://docs.google.com/document/d/170R8l0su_jjK_igha7evuvO341EeA1G8vX2RH5uijR0/edit?usp=sharing).

### Frontend Development

The frontend is a Next.js application with TypeScript. Key features:
- Type-safe API calls
- Real-time updates
- Responsive design with TailwindCSS

Directory structure:
- `src/app/`: Next.js app directory with pages
- `src/components/`: Components directory
- `src/interfaces/`: TypeScript interfaces for type safety
- `src/lib/`: Utility functions and API clients

### Backend Development

The backend is a FastAPI application with PostgreSQL. 

Directory structure:
- `app/main.py`: FastAPI application and routes
- `app/models.py`: SQLAlchemy database models
- `app/schemas.py`: Pydantic schemas for request/response validation
- `app/database.py`: Database configuration and connection

## API Endpoints

- `GET /`: Welcome message
- `GET /messages/`: List all messages
- `POST /messages/`: Create a new message


## Docker Configuration

The application uses Docker Compose to manage three services:
1. Frontend (Next.js)
2. Backend (FastAPI)
3. Database (PostgreSQL)

Each service has its own Dockerfile and is configured to work together through Docker networking.

