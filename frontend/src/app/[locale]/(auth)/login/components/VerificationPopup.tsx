'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useCallback, useEffect, useState, useRef } from 'react';
import { RotateCcw } from 'lucide-react';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { CreateUserRequest } from '@/interfaces/models/Auth';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/AuthService';
import { showErrorToast } from '@/lib/utils/toast';
import { handleInputChange, handleKeyDown, handlePasteEvent } from '@/lib/handlers/handleOtpInput';
import { api } from '@/services/ApiClient';

interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  signUpFormData: {
    fullName: string;
    email: string;
    phone_number: string;
    password: string;
    terms: boolean;
  };
}

export function VerificationPopup({ isOpen, onClose, signUpFormData }: VerificationPopupProps) {
  const t = useTranslations('Login.VerificationPopup');
  const tCommon = useTranslations('Common');
  const tLogin = useTranslations('Login');
  const [isLoading, setIsLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [error, setError] = useState<string | null>();
  const [verificationSent, setVerificationSent] = useState(false);

  const router = useRouter();

  const verificationSchema = z.object({
    code: z.string().length(6, tLogin('codeLengthError')),
  });
  const codeSize = 6;

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

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

  const sendInitialVerificationCode = useCallback(async () => {
    try {
      setIsLoading(true);
      await authService.sendVerificationCode(api, {
        phoneNumber: signUpFormData.phone_number,
      });
      setVerificationSent(true);
      setResendCooldown(30);
    } catch (err) {
      setError(t(`sendCodeError${err}`));
    } finally {
      setIsLoading(false);
    }
  }, [signUpFormData.phone_number, t]); // add dependencies the function uses

  useEffect(() => {
    if (isOpen && !verificationSent) {
      sendInitialVerificationCode();
    }
  }, [isOpen, verificationSent, sendInitialVerificationCode]);

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // First verify the code
      await authService.verifyCode(api, {
        phoneNumber: signUpFormData.phone_number,
        code: form.getValues('code'),
      });

      // If verification successful, create the user
      const data: CreateUserRequest = {
        fullName: signUpFormData.fullName,
        email: signUpFormData.email,
        phone: signUpFormData.phone_number,
        password: signUpFormData.password,
        // code: form.getValues('code'),
      };
      await authService.createUser(api, data);
      setIsLoading(false);

      router.push(`/confirm?email=${encodeURIComponent(signUpFormData.email)}`);
    } catch (err) {
      setError(err instanceof z.ZodError ? err.errors[0].message : tCommon('genericError'));
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (resendCooldown > 0) return;
    try {
      setIsLoading(true);
      await authService.sendVerificationCode(api, {
        phoneNumber: signUpFormData.phone_number,
      });
      setResendCooldown(30);
    } catch (err) {
      setError(t(`sendCodeError${err}`));
    } finally {
      setIsLoading(false);
    }
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
                <strong>{signUpFormData?.phone_number}</strong>
                {t('descriptionPartTwo')}
              </p>

              <FormField
                control={form.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-center">{tLogin('codeInputLabel')}</FormLabel>

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
                          onChange={(e) =>
                            handleInputChange(e, field, idx, codeSize, inputRefs.current)
                          }
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
                disabled={isLoading || form.watch('code').length !== codeSize}
                className={
                  isLoading || form.watch('code').length !== codeSize
                    ? 'bg-gray-400 hover:bg-gray-400'
                    : ''
                }
              >
                {isLoading ? tLogin('verifying') : tLogin('verify')}
              </Button>
              <Button size="full" variant="secondary" onClick={onClose} disabled={isLoading}>
                {tCommon('cancel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
