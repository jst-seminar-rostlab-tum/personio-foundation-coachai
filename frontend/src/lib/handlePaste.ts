interface PasteField {
  onChange: (code: string) => void;
  value?: string;
}

export function handlePasteEvent(
  e: React.ClipboardEvent<HTMLInputElement>,
  field: PasteField,
  codeSize: number,
  idPrefix = 'code-cell-'
): void {
  e.preventDefault();
  const pastedText = e.clipboardData.getData('text');
  const numericOnly = pastedText.replace(/\D/g, '');
  const codeToUse = numericOnly.slice(0, codeSize);

  if (codeToUse.length > 0) {
    field.onChange(codeToUse);
    const nextIndex = Math.min(codeToUse.length, codeSize - 1);
    const nextEl = document.getElementById(`${idPrefix}${nextIndex}`);
    (nextEl as HTMLInputElement)?.focus();
  }
}
