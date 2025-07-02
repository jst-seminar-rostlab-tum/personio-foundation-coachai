'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Checkbox from '@/components/ui/Checkbox';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/Form';
import { VerificationPopup } from '@/app/[locale]/(auth)/login/components/VerificationPopup';
import {
  PasswordInput,
  PasswordRequirement,
} from '@/app/[locale]/(auth)/login/components/PasswordInput';
import PrivacyDialog from '@/app/[locale]/(auth)/login/components/PrivacyDialog';
import { showErrorToast } from '@/lib/toast';
import Link from 'next/link';

export function SignUpForm() {
  const tLogin = useTranslations('Login');
  const [isLoading, setIsLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  const [showPrivacyDialog, setShowPrivacyDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const signUpFormSchema = z.object({
    fullName: z.string().min(1, tLogin('fullNameInputError')),
    email: z.string().email(tLogin('emailInputError')),
    phone_number: z.string().regex(/^\+[1-9]\d{7,14}$/, tLogin('phoneNumberInputError')),
    password: z
      .string()
      .regex(/^.{8,}$/)
      .regex(/[A-Z]/)
      .regex(/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/),
    terms: z.boolean().refine((val) => val === true),
  });

  const signUpForm = useForm({
    resolver: zodResolver(signUpFormSchema),
    mode: 'onTouched',
    defaultValues: {
      fullName: '',
      email: '',
      phone_number: '',
      password: '',
      terms: false,
    },
  });

  const passwordRequirements: PasswordRequirement[] = [
    {
      id: 'length',
      label: tLogin('SignUpTab.passwordInputRequirementOneLabel'),
      test: (password: string) => password.length >= 8,
    },
    {
      id: 'uppercase',
      label: tLogin('SignUpTab.passwordInputRequirementTwoLabel'),
      test: (password: string) => /[A-Z]/.test(password),
    },
    {
      id: 'special',
      label: tLogin('SignUpTab.passwordInputRequirementThreeLabel'),
      test: (password: string) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password),
    },
  ];

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleSubmit = async (values: z.infer<typeof signUpFormSchema>) => {
    setError(null);
    setIsLoading(true);

    setShowVerification(true);

    setIsLoading(false);
  };

  return (
    <>
      <Card className="shadow-none">
        <Form {...signUpForm}>
          <form onSubmit={signUpForm.handleSubmit(handleSubmit)}>
            <CardContent className="space-y-6 p-0">
              <FormField
                control={signUpForm.control}
                name="fullName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{tLogin('fullNameInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={tLogin('fullNameInputPlaceholder')}
                        {...field}
                        className="w-full"
                        disabled={isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={signUpForm.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{tLogin('emailInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={tLogin('emailInputPlaceholder')}
                        {...field}
                        className="w-full"
                        type="email"
                        disabled={isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={signUpForm.control}
                name="phone_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{tLogin('phoneNumberInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={tLogin('phoneNumberInputPlaceholder')}
                        {...field}
                        className="w-full"
                        type="tel"
                        disabled={isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={signUpForm.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{tLogin('passwordInputLabel')}</FormLabel>
                    <FormControl>
                      <PasswordInput
                        placeholder={tLogin('passwordInputPlaceholder')}
                        disabled={isLoading}
                        requirements={passwordRequirements}
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <Card className="shadow-none border border-bw-30 p-2">
                <CardContent className="p-1">
                  <p className="text-base">
                    {tLogin('SignUpTab.gdprAdherenceText')}
                    <Button
                      variant="link"
                      type="button"
                      className="h-auto p-0 text-blue-600 hover:text-blue-800 underline"
                      onClick={() => setShowPrivacyDialog(true)}
                    >
                      {tLogin('SignUpTab.readMoreOnGdprLink')}
                    </Button>
                  </p>
                </CardContent>
              </Card>

              <FormField
                control={signUpForm.control}
                name="terms"
                render={({ field }) => (
                  <FormItem className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onClick={() => field.onChange(!field.value)}
                          disabled={isLoading}
                        />
                      </FormControl>
                      <FormLabel className="text-sm">
                        {tLogin.rich('SignUpTab.agreeToTermsCheckboxLabel', {
                          terms: (chunks) => (
                            <Link
                              href="/terms"
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 underline"
                            >
                              {chunks}
                            </Link>
                          ),
                          privacy: (chunks) => (
                            <Link
                              href="/privacy"
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 underline"
                            >
                              {chunks}
                            </Link>
                          ),
                        })}
                      </FormLabel>
                    </div>
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter className="flex-col gap-6">
              <Button size="full" type="submit" disabled={isLoading}>
                {tLogin('signUp')}
              </Button>
              <div className="w-full border-t border-gray-300" />
              <Button size="full" variant="secondary" disabled={isLoading}>
                <Image
                  src="/images/icons/google-icon.svg"
                  alt="Google Icon"
                  width={20}
                  height={20}
                />
                {tLogin('SignUpTab.signUpWithGoogleButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>

      <VerificationPopup
        isOpen={showVerification}
        onClose={() => setShowVerification(false)}
        signUpFormData={signUpForm.getValues()}
      />

      <PrivacyDialog open={showPrivacyDialog} onOpenChange={setShowPrivacyDialog}></PrivacyDialog>
    </>
  );
}
