'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import Input from '@/components/ui/Input';
import { handlePasteEvent } from '@/lib/handlePaste';
import { createClient } from '@/lib/supabase/client';
import { showErrorToast } from '@/lib/toast';
import { api } from '@/services/ApiClient';
import { authService } from '@/services/AuthService';
import { zodResolver } from '@hookform/resolvers/zod';
import { ResendParams, VerifyEmailOtpParams } from '@supabase/supabase-js';
import { useTranslations } from 'next-intl';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import z from 'zod';
import { UserProfileService } from '@/services/UserProfileService';

export default function ConfirmationForm() {
  const t = useTranslations('Confirm.ConfirmationForm');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>();
  const [showResendButton, setShowResendButton] = useState(false);

  const router = useRouter();

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const hasDeletedRef = useRef(false);
  const isConfirmedRef = useRef(false);

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const confirmationFormSchema = z.object({
    email: z.string().email(t('emailInputError')),
    code: z.string(),
  });
  const codeSize = 6;

  const form = useForm({
    resolver: zodResolver(confirmationFormSchema),
    mode: 'onTouched',
    defaultValues: {
      email: useSearchParams().get('email') ?? '',
      code: useSearchParams().get('token') ?? '',
    },
  });

  const verifyOTP = async () => {
    setIsLoading(true);
    setError(null);

    const formData = confirmationFormSchema.parse(form.getValues());
    const supabase = await createClient();
    const params: VerifyEmailOtpParams = {
      email: formData.email,
      token: formData.code,
      type: 'signup',
    };
    const { error: verifyError } = await supabase.auth.verifyOtp(params);
    if (verifyError) {
      setError(verifyError.message);
      setIsLoading(false);

      if (verifyError.code) {
        switch (verifyError.code) {
          case 'otp_expired':
            setError(t('expiredOtpError'));
            setShowResendButton(true);
            break;
          default:
            setError(t('genericError'));
        }
      }

      return;
    }

    try {
      await authService.confirmUser(api);
      isConfirmedRef.current = true;
    } catch {
      setError(t('genericError'));
      setIsLoading(false);
      return;
    }

    router.push('/onboarding');
  };

  const resendConfirmationEmail = async () => {
    setIsLoading(true);
    setError(null);

    form.setValue('code', '');
    const formData = confirmationFormSchema.parse(form.getValues());
    const supabase = await createClient();
    const credentials: ResendParams = {
      email: formData.email,
      type: 'signup',
    };
    const { error: resendError } = await supabase.auth.resend(credentials);
    if (resendError) {
      setError(resendError.message);
      setIsLoading(false);
      return;
    }

    setIsLoading(false);
    setShowResendButton(false);
  };

  useEffect(() => {
    const handleDelete = async () => {
      const email = form.getValues('email');
      if (!email || hasDeletedRef.current || isConfirmedRef.current) return;
      hasDeletedRef.current = true;
      try {
        await UserProfileService.deleteUnconfirmedUser(api, email);
      } catch {
        // Optionally handle/log error
      }
    };

    const handleUrlChange = () => {
      handleDelete();
    };

    window.addEventListener('popstate', handleUrlChange);
    window.addEventListener('hashchange', handleUrlChange);
    window.addEventListener('beforeunload', handleDelete);

    return () => {
      window.removeEventListener('popstate', handleUrlChange);
      window.removeEventListener('hashchange', handleUrlChange);
      window.removeEventListener('beforeunload', handleDelete);
      handleDelete(); // Always attempt on unmount
    };
  }, [form]);

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <Card className="relative w-[90%] max-w-sm border-0 bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(verifyOTP)}>
            <CardContent className="space-y-4 p-4">
              <h2 className="text-xl text-center">{t('title')}</h2>
              <p className="text-base text-center text-bw-50">
                {!showResendButton ? t('description') : t('expiredDescription')}
              </p>

              {!showResendButton && (
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
                            disabled={isLoading}
                            value={field.value[idx] || ''}
                            ref={(el) => {
                              inputRefs.current[idx] = el;
                            }}
                            onChange={(e) => {
                              const val = e.target.value.replace(/\D/g, '');
                              const codeArr = (field.value || '').split('');
                              codeArr[idx] = val;
                              const newCode = codeArr.join('').slice(0, codeSize);
                              field.onChange(newCode);
                              if (val && idx < codeSize - 1) {
                                inputRefs.current[idx + 1]?.focus();
                              }
                            }}
                            onPaste={(e) => {
                              handlePasteEvent(e, field, codeSize, inputRefs.current);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Backspace') {
                                const codeArr = (field.value || '').split('');
                                if (!codeArr[idx] && idx > 0) {
                                  inputRefs.current[idx - 1]?.focus();
                                }
                              }
                            }}
                            autoFocus={idx === 0}
                          />
                        ))}
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <FormMessage />
            </CardContent>
            <CardFooter className="flex-col gap-2 p-4">
              {!showResendButton && (
                <Button
                  size="full"
                  type="submit"
                  disabled={isLoading || form.watch('code').length !== codeSize}
                >
                  {isLoading ? t('confirmingButtonLabel') : t('confirmButtonLabel')}
                </Button>
              )}

              {showResendButton && (
                <Button
                  size="full"
                  type="button"
                  onClick={resendConfirmationEmail}
                  disabled={isLoading}
                >
                  {t('resendCodeButtonLabel')}
                </Button>
              )}
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
