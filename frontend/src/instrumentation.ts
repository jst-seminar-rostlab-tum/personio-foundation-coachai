import * as Sentry from '@sentry/nextjs';

/**
 * Registers runtime-specific Sentry configuration.
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('../sentry.server.config');
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('../sentry.edge.config');
  }
}

/**
 * Reports request errors to Sentry.
 */
export const onRequestError = Sentry.captureRequestError;
