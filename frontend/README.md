# Next.js Frontend

## Project Structure

```
frontend/
├─ src/
│  ├─ app/                      # Next.js App Router (routes, layouts, handlers)
│  │  ├─ api/                   # Route handlers / API routes
│  │  └─ [locale]/              # Locale-specific routes
│  │     ├─ (about)/            # Route group: about pages
│  │     ├─ (auth)/             # Route group: authentication
│  │     ├─ (main)/             # Route group: main app pages
│  │     └─ (standalone)/       # Route group: standalone pages
│  ├─ components/               # Reusable UI components
│  ├─ contexts/                 # React contexts
│  ├─ i18n/                     # i18n setup and helpers
│  ├─ interfaces/               # Shared TypeScript interfaces
│  ├─ lib/                      # Utilities, constants, supabase, handlers
│  ├─ services/                 # API clients and domain services
│  ├─ store/                    # Zustand stores
│  ├─ styles/                   # Global styles
│  ├─ instrumentation.ts        # Server-side instrumentation (Sentry)
│  ├─ instrumentation-client.ts # Client-side instrumentation (Sentry)
│  └─ middleware.ts             # Next.js middleware
├─ public/                      # Static assets
├─ messages/                    # i18n message catalogs (en/de)
├─ __tests__/                   # Unit/integration tests
├─ Dockerfile                   # Frontend container build
├─ next.config.ts               # Next.js configuration
├─ package.json                 # NPM scripts and dependencies
└─ README.md                    # Frontend documentation
```

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
- `NEXT_PUBLIC_SKIP_EMAIL_VERIFICATION`: Skip email verification during signup

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

## Test Signup Locally

1. In `supabase\config.toml` set `enable_confirmations` under `[auth.email]` to `true`.
2. Restart your local supabase instance (see backend readme).
3. In your frontend `.env` file, set `NEXT_PUBLIC_SKIP_EMAIL_VERIFICATION` to `"false"`, and restart the frontend.
4. Visit the login page and complete all signup steps until you have to enter the email verification code.
5. Visit the email smtp server of your local supabase instance. By default this is reachable under `http://localhost:54324/`
6. Search for the verification code corresponding to your email and enter it on the login page.
