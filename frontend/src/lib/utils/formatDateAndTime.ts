export const formattedDate = (date: string | undefined, locale: string) => {
  if (!date) return '';

  return new Date(date).toLocaleDateString(locale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

export const formattedDateTime = (date: string | undefined, locale: string) => {
  if (!date) return '';
  // Use en-GB for English to avoid American date format
  const effectiveLocale = locale === 'en' ? 'en-GB' : locale;
  return new Date(date).toLocaleString(effectiveLocale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
};
