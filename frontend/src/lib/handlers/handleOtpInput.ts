/**
 * Field interface for OTP input updates.
 */
interface PasteField {
  onChange: (code: string) => void;
  value?: string;
}

/**
 * Handles pasting OTP codes into the input group.
 */
export function handlePasteEvent(
  e: React.ClipboardEvent<HTMLInputElement>,
  field: PasteField,
  codeSize: number,
  inputRefs: (HTMLInputElement | null)[]
): void {
  e.preventDefault();
  const pastedText = e.clipboardData.getData('text');
  const numericOnly = pastedText.replace(/\D/g, '');
  const codeToUse = numericOnly.slice(0, codeSize);

  if (codeToUse.length > 0) {
    field.onChange(codeToUse);
    const nextIndex = Math.min(codeToUse.length, codeSize - 1);
    const nextEl = inputRefs[nextIndex];
    nextEl?.focus();
  }
}

/**
 * Handles individual OTP input changes and focus movement.
 */
export function handleInputChange(
  e: React.ChangeEvent<HTMLInputElement>,
  field: PasteField,
  idx: number,
  codeSize: number,
  inputRefs: (HTMLInputElement | null)[]
): void {
  const val = e.target.value.replace(/\D/g, '');
  const codeArr = (field.value || '').split('');
  codeArr[idx] = val;
  const newCode = codeArr.join('').slice(0, codeSize);
  field.onChange(newCode);
  if (val && idx < codeSize - 1) {
    inputRefs[idx + 1]?.focus();
  }
}

/**
 * Handles backspace navigation across OTP inputs.
 */
export function handleKeyDown(
  e: React.KeyboardEvent<HTMLInputElement>,
  field: PasteField,
  idx: number,
  inputRefs: (HTMLInputElement | null)[]
): void {
  if (e.key === 'Backspace') {
    const codeArr = (field.value || '').split('');
    if (!codeArr[idx] && idx > 0) {
      inputRefs[idx - 1]?.focus();
    }
  }
}
