'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState, useRef } from 'react';
import { RotateCcw } from 'lucide-react';
import { Form, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/Form';
import { UserCreate } from '@/interfaces/models/Auth';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/AuthService';
import { showErrorToast } from '@/lib/utils/toast';
import { handleInputChange, handleKeyDown, handlePasteEvent } from '@/lib/handlers/handleOtpInput';
import { api } from '@/services/ApiClient';
import axios from 'axios';
import { createClient } from '@/lib/supabase/client';
import { SignInWithPasswordCredentials } from '@supabase/supabase-js';
import { SKIP_EMAIL_VERIFICATION } from '@/lib/connector';

interface PhoneNumberVerificationPopupProps {
  onClose: () => void;
  signUpFormData: {
    fullName: string;
    email: string;
    phone_number: string;
    organizationName?: string;
    nonprofitStatus: 'yes' | 'no';
    password: string;
    terms: boolean;
  };
  onSuccess: () => void;
}

export function PhoneNumberVerificationPopup({
  onClose,
  signUpFormData,
  onSuccess,
}: PhoneNumberVerificationPopupProps) {
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

  useEffect(() => {
    if (!verificationSent) {
      handleSendVerificationCode();
    }
  });

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const handleSendVerificationCode = async () => {
    if (resendCooldown > 0) return;
    try {
      setIsLoading(true);
      await authService.sendVerificationCode(api, {
        phoneNumber: signUpFormData.phone_number,
      });
      setVerificationSent(true);
      setResendCooldown(30);
    } catch (err) {
      console.error(err);
      setError(t(`errorResend`));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    const data: UserCreate = {
      fullName: signUpFormData.fullName,
      email: signUpFormData.email,
      phone: signUpFormData.phone_number,
      verificationCode: form.getValues('code'),
      password: signUpFormData.password,
      organizationName:
        signUpFormData.nonprofitStatus === 'yes' ? signUpFormData.organizationName : undefined,
    };

    try {
      await authService.signUpUser(api, data);
      const supabase = await createClient();
      const credentials: SignInWithPasswordCredentials = {
        email: signUpFormData.email,
        password: signUpFormData.password,
      };

      if (SKIP_EMAIL_VERIFICATION) {
        await supabase.auth.signInWithPassword(credentials);
        router.push('/onboarding');
      } else {
        onSuccess();
      }

      setIsLoading(false);
    } catch (err) {
      let message = tCommon('genericError');

      if (err instanceof z.ZodError) {
        message = err.errors[0].message;
      } else if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        if (typeof detail === 'string' && detail.includes('Phone number already registered')) {
          message = tCommon('numberInUseError');
        }
      }
      setError(message);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <Card className="relative w-[90%] max-w-sm border-0 animate-in fade-in zoom-in duration-200">
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
                  onClick={handleSendVerificationCode}
                  disabled={resendCooldown > 0 || isLoading}
                  className={`text-base p-0 h-auto font-normal transition-colors flex items-center gap-1 ${
                    resendCooldown > 0 || isLoading
                      ? 'text-bw-70 cursor-not-allowed'
                      : 'text-forest-90 cursor-pointer'
                  }`}
                >
                  <RotateCcw
                    size={14}
                    className={`${resendCooldown > 0 ? 'animate-spin [animation-direction:reverse]' : ''} ${
                      resendCooldown > 0 || isLoading ? 'text-gray-bw-40' : 'text-forest-90'
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
              <Button size="full" onClick={onClose} disabled={isLoading}>
                {tCommon('cancel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
