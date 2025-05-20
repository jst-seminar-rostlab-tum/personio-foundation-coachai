import { defineRouting } from 'next-intl/routing';

const routing = defineRouting({
  locales: ['en', 'de'],
  defaultLocale: 'en',
});

export default routing;
