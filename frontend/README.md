# Next.js Frontend

## Setup

### Local Development

1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run dev
```

### Docker Development

The frontend service is containerized using Docker. You can run it using Docker Compose:

```bash
docker compose up frontend
```

## API Integration

The frontend communicates with the backend API using the Fetch API. Key endpoints:

- `GET /messages/`: Fetch all messages
- `POST /messages/`: Create a new message

## Environment Variables

The following environment variables can be configured:

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Development Tools

- **TypeScript**: For type safety
- **Next.js**: For server-side rendering and routing
- **TailwindCSS**: For styling
- **ESLint**: For code linting
- **SWR**: For data fetching

## Code Style

This project uses ESLint to enforce linting rules and Prettier to automatically format your code.

## Deployment

The application can be deployed using Docker:

```bash
docker build -t frontend .
docker run -p 3000:3000 frontend
```

Or using Docker Compose:

```bash
docker compose up frontend
```
