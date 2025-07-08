'use client';

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import Input from '@/components/ui/Input';
import { handleInputChange, handleKeyDown, handlePasteEvent } from '@/lib/handlers/handleOtpInput';
import { createClient } from '@/lib/supabase/client';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { authService } from '@/services/AuthService';
import { zodResolver } from '@hookform/resolvers/zod';
import { ResendParams, VerifyEmailOtpParams } from '@supabase/supabase-js';
import { useTranslations } from 'next-intl';
import { useSearchParams, useRouter } from 'next/navigation';
import { useEffect, useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import z from 'zod';

export default function ConfirmationForm() {
  const t = useTranslations('Login');
  const tCommon = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>();
  const [showResendButton, setShowResendButton] = useState(false);

  const router = useRouter();

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const confirmationFormSchema = z.object({
    email: z.string().email(tCommon('emailInputError')),
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
            setError(t('ConfirmationForm.expiredOtpError'));
            setShowResendButton(true);
            break;
          default:
            setError(t('ConfirmationForm.genericError'));
        }
      }

      return;
    }

    try {
      await authService.confirmUser(api);
    } catch {
      setError(t('ConfirmationForm.genericError'));
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

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <Card className="relative w-[90%] max-w-sm border-0 bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(verifyOTP)}>
            <CardContent className="space-y-4 p-4">
              <h2 className="text-xl text-center">{t('ConfirmationForm.title')}</h2>
              <p className="text-base text-center text-bw-50">
                {!showResendButton
                  ? t('ConfirmationForm.description')
                  : t('ConfirmationForm.expiredDescription')}
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
                              handleInputChange(e, field, idx, codeSize, inputRefs.current);
                            }}
                            onPaste={(e) => {
                              handlePasteEvent(e, field, codeSize, inputRefs.current);
                            }}
                            onKeyDown={(e) => {
                              handleKeyDown(e, field, idx, inputRefs.current);
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
                  {isLoading ? t('confirming') : tCommon('confirm')}
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
