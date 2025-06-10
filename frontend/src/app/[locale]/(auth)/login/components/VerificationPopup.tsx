'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { AlertCircleIcon, RotateCcw } from 'lucide-react';
import { VerificationPopupProps } from '@/interfaces/VerificationPopup';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { Alert, AlertTitle } from '@/components/ui/Alert';
import { CreateUserRequest } from '@/interfaces/auth/CreateUserRequest';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/auth.service';

export function VerificationPopup({ isOpen, onClose, signUpFormData }: VerificationPopupProps) {
  const t = useTranslations('Login.VerificationPopup');
  const [isLoading, setIsLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [error, setError] = useState<string | null>();

  const router = useRouter();

  const verificationSchema = z.object({
    code: z.string(),
  });
  const codeSize = 6;

  const form = useForm({
    resolver: zodResolver(verificationSchema),
    mode: 'onTouched',
    defaultValues: {
      code: '',
    },
  });

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (resendCooldown > 0) {
      timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data: CreateUserRequest = {
        full_name: signUpFormData.fullName,
        email: signUpFormData.email,
        phone: signUpFormData.phoneNumber,
        password: signUpFormData.password,
        code: form.getValues('code'),
      };
      await authService.create(data);
      setIsLoading(false);
      router.push(`/confirm?email=${encodeURIComponent(signUpFormData.email)}`);
    } catch (err) {
      setError(err instanceof z.ZodError ? err.errors[0].message : t('genericError'));
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setResendCooldown(30);
    // TODO: Call API to resend verification code (services/Api.ts)
    // TODO: setError if Api call failed
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <Card className="relative w-[90%] max-w-sm border-0 bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)}>
            <CardContent className="space-y-4 p-4">
              <h2 className="text-xl text-center">{t('title')}</h2>
              <p className="text-base text-center text-bw-50">
                {t('descriptionPartOne')}
                <strong>{signUpFormData?.phoneNumber}</strong>
                {t('descriptionPartTwo')}
              </p>

              <FormField
                control={form.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-center">{t('codeInputLabel')}</FormLabel>

                    <div className="flex justify-center gap-2">
                      {[...Array(codeSize)].map((_, idx) => (
                        <Input
                          key={idx}
                          type="text"
                          inputMode="numeric"
                          maxLength={1}
                          className="w-10 text-center text-lg"
                          disabled={isLoading || resendCooldown > 0}
                          value={field.value[idx] || ''}
                          onChange={(e) => {
                            const val = e.target.value.replace(/\D/g, '');
                            const codeArr = (field.value || '').split('');
                            codeArr[idx] = val;
                            const newCode = codeArr.join('').slice(0, codeSize);
                            field.onChange(newCode);
                            if (val && idx < codeSize - 1) {
                              const next = document.getElementById(`code-cell-${idx + 1}`);
                              (next as HTMLInputElement)?.focus();
                            }
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Backspace') {
                              const codeArr = (field.value || '').split('');
                              if (!codeArr[idx] && idx > 0) {
                                const prev = document.getElementById(`code-cell-${idx - 1}`);
                                (prev as HTMLInputElement)?.focus();
                              }
                            }
                          }}
                          id={`code-cell-${idx}`}
                          autoFocus={idx === 0}
                        />
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormMessage />

              <div className="flex justify-center">
                <Button
                  type="button"
                  variant="ghost"
                  size="default"
                  onClick={handleResendCode}
                  disabled={resendCooldown > 0 || isLoading}
                  className={`text-base p-0 h-auto font-normal transition-colors flex items-center gap-1 ${
                    resendCooldown > 0 || isLoading
                      ? 'text-bw-40 cursor-not-allowed'
                      : 'text-marigold-50 cursor-pointer'
                  }`}
                >
                  <RotateCcw
                    size={14}
                    className={`${resendCooldown > 0 ? 'animate-spin' : ''} ${
                      resendCooldown > 0 || isLoading ? 'text-gray-bw-40' : 'text-marigold-50'
                    }`}
                  />
                  {`${t('resendButtonLabel')}${resendCooldown > 0 ? ` (${resendCooldown}s)` : ''}`}
                </Button>
              </div>
            </CardContent>
            <CardFooter className="flex-col gap-2 p-4">
              <Button
                size="full"
                type="submit"
                disabled={isLoading || resendCooldown > 0 || form.watch('code').length !== codeSize}
              >
                {isLoading ? t('verifyingButtonLabel') : t('verifyButtonLabel')}
              </Button>
              <Button size="full" variant="secondary" onClick={onClose} disabled={isLoading}>
                {t('cancelButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircleIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      )}
    </div>
  );
}
