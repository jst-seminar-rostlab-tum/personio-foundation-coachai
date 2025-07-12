export const formatDateFlexible = (
  date: string | undefined,
  locale: string,
  showTime: boolean = false
) => {
  if (!date) return '';
  const effectiveLocale = locale === 'en' ? 'en-GB' : locale;
  const options: Intl.DateTimeFormatOptions = showTime
    ? {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }
    : {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      };
  return new Date(date).toLocaleString(effectiveLocale, options);
};
