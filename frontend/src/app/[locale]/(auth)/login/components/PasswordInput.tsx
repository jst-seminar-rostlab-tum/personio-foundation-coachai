import { useState } from 'react';
import { EyeIcon, EyeOffIcon, CheckIcon, XIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';
import { PasswordInputProps } from '@/interfaces/PasswordInput';
import Input from '@/components/ui/Input';

export function PasswordInput({
  placeholder,
  disabled,
  requirements,
  onChange,
  ...props
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [passwordValue, setPasswordValue] = useState('');
  const t = useTranslations('Login.PasswordInput');

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setPasswordValue(newValue);
    onChange?.(e);
  };

  return (
    <div className="space-y-2 text-base">
      <div className="relative">
        <Input
          placeholder={placeholder}
          disabled={disabled}
          type={showPassword ? 'text' : 'password'}
          className="w-full"
          {...props}
          onChange={handlePasswordChange}
        />
        <button
          type="button"
          className="absolute right-2 top-1/2 -translate-y-1/2 focus:outline-none cursor-pointer"
          onClick={() => setShowPassword(!showPassword)}
        >
          {showPassword ? <EyeOffIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
          <span className="sr-only">
            {showPassword ? t("hidePasswordSpan") : t('showPasswordSpan')}
          </span>
        </button>
      </div>

      {requirements && (
        <div className="mt-2 space-y-1">
          <ul className="space-y-1">
            {requirements.map((requirement) => {
              const isMet = requirement.test(passwordValue);
              return (
                <li key={requirement.id} className="flex items-center gap-2">
                  <div className={cn(isMet ? 'text-forest-50' : 'text-flame-50')}>
                    {isMet ? (
                      <CheckIcon className="w-3 h-3" color="currentColor" strokeWidth={4} />
                    ) : (
                      <XIcon className="w-3 h-3" color="currentColor" strokeWidth={4} />
                    )}
                  </div>
                  <span>{requirement.label}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
