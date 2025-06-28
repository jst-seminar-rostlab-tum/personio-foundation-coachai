'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
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
import { PasswordInput } from '@/app/[locale]/(auth)/login/components/PasswordInput';
import { createClient } from '@/lib/supabase/client';
import { SignInWithPasswordCredentials } from '@supabase/supabase-js';
import { useRouter } from 'next/navigation';
import { showErrorToast } from '@/lib/toast';

export function SignInForm() {
  const t = useTranslations('Login.SignInTab');
  const tLogin = useTranslations('Login');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const signInFormSchema = z.object({
    email: z.string().email(tLogin('emailInputError')),
    password: z.string().min(1, tLogin('passwordInputError')),
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

    const formData = signInFormSchema.parse(values);
    const supabase = await createClient();
    const credentials: SignInWithPasswordCredentials = {
      email: formData.email,
      password: formData.password,
    };
    const response = await supabase.auth.signInWithPassword(credentials);
    if (response.error) {
      setError(response.error.message);
      setIsLoading(false);
      return;
    }

    router.push('/dashboard');
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
              control={signInForm.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{tLogin('passwordInputLabel')}</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder={tLogin('passwordInputPlaceholder')}
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
              {tLogin('signIn')}
            </Button>
            <div className="w-full border-t border-gray-300" />
            <Button size="full" variant="secondary" disabled={isLoading}>
              <Image src="/images/icons/google-icon.svg" alt="Google Icon" width={20} height={20} />
              {t('signInWithGoogleButtonLabel')}
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
