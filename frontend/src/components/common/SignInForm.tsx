'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import Image from 'next/image';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/Form';
import { AlertCircleIcon } from 'lucide-react';
import { PasswordInput } from './PasswordInput';
import { Alert, AlertTitle } from '../ui/Alert';

export function SignInForm() {
  const t = useTranslations('Login.SignInTab');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const signInFormSchema = z.object({
    email: z.string().email(t('emailInputError')),
    password: z.string().min(1, t('passwordInputError')),
  });

  const signInForm = useForm({
    resolver: zodResolver(signInFormSchema),
    mode: 'onTouched',
    defaultValues: {
      email: '',
      password: '',
    },
  });

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleSubmit = async (values: z.infer<typeof signInFormSchema>) => {
    setError(null);
    setIsLoading(true);
    // TODO: Call API to sign in the user with email and password (services/Api.ts)
    // TODO: Reroute if Api call successfull and setErrors if failed
    setIsLoading(false);
  };

  return (
    <Card className="shadow-none">
      <Form {...signInForm}>
        <form onSubmit={signInForm.handleSubmit(handleSubmit)}>
          <CardContent className="space-y-6 p-0">
            {error && <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">{error}</div>}

            <FormField
              control={signInForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('emailInputLabel')}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={t('emailInputPlaceholder')}
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
              control={signInForm.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t('passwordInputLabel')}</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder={t('passwordInputPlaceholder')}
                      {...field}
                      disabled={isLoading}
                      requirements={[]}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </CardContent>

          <CardFooter className="flex-col gap-6">
            <Button type="submit" size="full" disabled={isLoading}>
              {t('signInButtonLabel')}
            </Button>
            <div className="w-full border-t border-gray-300" />
            <Button size="full" variant="secondary" disabled={isLoading}>
              <Image
                src="/icons/google-icon.svg"
                alt="Google Icon"
                className="mr-2"
                width={5}
                height={5}
              ></Image>
              {t('signInWithGoogleButtonLabel')}
            </Button>
          </CardFooter>
        </form>
      </Form>

      {error && (
        <Alert variant="destructive">
          <AlertCircleIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      )}
    </Card>
  );
}
