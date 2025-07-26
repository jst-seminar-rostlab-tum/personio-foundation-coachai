# Next.js Frontend

## Setup

Copy the .env.example into your .env.
The .env.example is designed for local usage.

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

The frontend communicates with the backend API through service layers. Key services:

- `AuthService`: Authentication and user management
- `ConversationScenarioService`: Conversation scenario management
- `SessionService`: Session handling and real-time communication
- `ReviewService`: Review functionality
- `UserProfileService`: User profile management
- `AdminService`: Admin dashboard functionality
- `ResourceService`: Resource management

The application uses Supabase for authentication and real-time features.

## API Client Architecture

The frontend uses two Axios instances: `ApiClient` for browser-side requests and `ApiServer` for server-side requests, both with automatic authentication via `AuthInterceptor`.

## Environment Variables

The following environment variables can be configured:

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anonymous key
- `NEXT_PUBLIC_BASE_URL`: Base URL for the application 
- `NEXT_PUBLIC_DEV_MODE_SKIP_AUTH`: Skip authentication in development mode

## Development Tools

- **TypeScript**: For type safety
- **Next.js 15.3.2**: For server-side rendering and routing with App Router
- **TailwindCSS v4**: For styling
- **ESLint**: For code linting
- **Prettier**: For auto formatting
- **Axios**: For HTTP requests with client/server separation
- **Supabase**: For authentication and backend services
- **Next-intl**: For internationalization (i18n)
- **Zustand**: For state management
- **React Hook Form**: For form handling with Zod validation
- **shadcn/ui**: For accessible UI components
- **Husky**: For git hooks

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
