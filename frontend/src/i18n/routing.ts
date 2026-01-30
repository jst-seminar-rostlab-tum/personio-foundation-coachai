import { defineRouting } from 'next-intl/routing';

/**
 * Locale routing configuration for the app.
 */
const routing = defineRouting({
  locales: ['en', 'de'],
  defaultLocale: 'en',
  localePrefix: 'as-needed',
});

export default routing;
