export const formatDateFlexible = (
  date: string | undefined,
  locale: string,
  showTime: boolean = false
) => {
  if (!date) return '';

  const effectiveLocale = locale === 'en' ? 'en-GB' : locale;
  const { timeZone } = Intl.DateTimeFormat().resolvedOptions();

  const options: Intl.DateTimeFormatOptions = showTime
    ? {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
        timeZone,
      }
    : {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone,
      };

  let parsedDate: Date;

  if (!showTime) {
    const [year, month, day] = date.split('-').map(Number);
    parsedDate = new Date(year, month - 1, day);
  } else {
    parsedDate = new Date(date.endsWith('Z') ? date : `${date}Z`);
  }

  return parsedDate.toLocaleString(effectiveLocale, options);
};
