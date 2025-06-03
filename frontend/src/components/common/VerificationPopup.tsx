import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { userProfileApi } from '@/services/Api';
import { RotateCcw } from 'lucide-react';
import { VerificationPopupProps } from '@/interfaces/VerificationPopup';
import { supabase } from '@/lib/supabase';

export function VerificationPopup({
  isOpen,
  onClose,
  recipientPhoneNumber,
  formData,
}: VerificationPopupProps) {
  const t = useTranslations('Login.VerificationPopup');
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [verificationCode] = useState('');

  const verificationSchema = z.object({
    code: z.string().regex(/^\d{6}$/, t('codeInputError')),
  });
  const codeSize = 6;
  // const reciepientPhone = '+491753288376';
  // const reciepientPhone = '+4915730709306';

  const form = useForm({
    resolver: zodResolver(verificationSchema),
    mode: 'onTouched',
    defaultValues: {
      code: '',
    },
  });

  const signIn = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Supabase verification
      const { error: signInError } = await supabase.auth.signInWithOtp({
        phone: recipientPhoneNumber,
      });

      if (signInError) {
        console.error('Supabase verification error:', signInError);
        throw signInError;
      }

      // Twilio verification (commented out but kept for reference)
      // await userProfileApi.sendVerificationCode(recipientPhoneNumber);
    } catch (err) {
      console.error('Error in sign in:', err);
      setError('Failed to send verification code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [recipientPhoneNumber]);

  const verifyCode = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Supabase verification
      const { error: verifyError } = await supabase.auth.verifyOtp({
        phone: recipientPhoneNumber,
        token: verificationCode,
        type: 'sms',
      });

      if (verifyError) {
        console.error('Supabase verification error:', verifyError);
        throw verifyError;
      }

      // Twilio verification (commented out but kept for reference)
      // const result = await userProfileApi.verifyCode(recipientPhoneNumber, verificationCode);
      // if (!result.valid) {
      //   throw new Error('Invalid verification code');
      // }

      onClose();
      router.push('/');
    } catch (err) {
      console.error('Error verifying code:', err);
      setError('Invalid verification code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (resendCooldown > 0) {
      timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  // Send verification code when popup opens
  useEffect(() => {
    if (isOpen) {
      signIn();
    }
  }, [isOpen, signIn]);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Verify the code
      verifyCode();
      const isVerified = true;

      if (!isVerified) {
        setError(t('invalidCode'));
        return;
      }

      // If verification successful and we have form data, create the user
      if (formData) {
        try {
          await userProfileApi.create({
            full_name: formData.fullName,
            email: formData.email,
            phone_number: formData.phoneNumber,
            password: formData.password,
            preferred_language: 'en',
            preferred_learning_style_id: '',
            preferred_session_length: '',
            role_id: undefined,
            experience_id: undefined,
          });

          // If we get here, user was created successfully
          onClose();
          router.push('/');
        } catch (err) {
          console.error('Error creating user:', err);
          setError(t('genericError'));
        }
      }
    } catch (err: unknown) {
      const errorMessage = t('genericError');
      console.error('Error verifying code:', err);

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      setError(null);
      await userProfileApi.sendVerificationCode(recipientPhoneNumber);
      setResendCooldown(30);
    } catch (err: unknown) {
      let errorMessage = t('resendError');

      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'data' in err.response &&
        err.response.data &&
        typeof err.response.data === 'object' &&
        'detail' in err.response.data
      ) {
        const { detail } = err.response.data;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail[0]?.msg || t('resendError');
        } else if (typeof detail === 'object' && detail !== null && 'msg' in detail) {
          errorMessage = String(detail.msg);
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <Card className="relative w-[90%] max-w-sm border-0 shadow-lg bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)}>
            <CardContent className="space-y-4 p-4">
              <h2 className="text-xl font-semibold text-center">{t('title')}</h2>
              <p className="text-sm text-center text-gray-600">
                {t('descriptionPartOne')}
                <strong>{recipientPhoneNumber}</strong>
                {t('descriptionPartTwo')}
              </p>

              {error && (
                <div className="p-2 text-sm text-red-500 bg-red-50 rounded-md">{error}</div>
              )}

              <FormField
                control={form.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm flex justify-center">
                      {t('codeInputLabel')}
                    </FormLabel>

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
                  className={`text-sm p-0 h-auto font-normal transition-colors flex items-center gap-1 ${
                    resendCooldown > 0 || isLoading
                      ? 'text-gray-400 cursor-not-allowed hover:text-gray-400'
                      : 'text-blue-600 hover:text-blue-700 cursor-pointer'
                  }`}
                >
                  <RotateCcw
                    size={14}
                    className={`${resendCooldown > 0 ? 'animate-spin' : ''} ${
                      resendCooldown > 0 || isLoading ? 'text-gray-400' : 'text-blue-600'
                    }`}
                  />
                  {`${t('resendButtonLabel')}${resendCooldown > 0 ? ` (${resendCooldown}s)` : ''}`}
                </Button>
              </div>
            </CardContent>
            <CardFooter className="flex-col gap-2 p-4">
              <Button
                size={'full'}
                type="submit"
                disabled={isLoading || resendCooldown > 0 || form.watch('code').length !== codeSize}
                className="disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? t('verifyingButtonLabel') : t('verifyButtonLabel')}
              </Button>
              <Button size={'full'} variant={'secondary'} onClick={onClose} disabled={isLoading}>
                {t('cancelButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
