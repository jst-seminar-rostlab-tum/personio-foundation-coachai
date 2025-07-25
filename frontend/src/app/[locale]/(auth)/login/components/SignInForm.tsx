'use client';

import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
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
import { showErrorToast } from '@/lib/utils/toast';
import ConfirmationForm from '@/app/[locale]/(auth)/login/components/ConfirmationForm';

export function SignInForm() {
  const tLogin = useTranslations('Login');
  const tCommon = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const signInFormSchema = z.object({
    email: z.string().email(tCommon('emailInputError')),
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
      // Check for unconfirmed email error
      if (
        response.error.message.toLowerCase().includes('confirm') ||
        response.error.message.toLowerCase().includes('verify')
      ) {
        setPendingEmail(formData.email);
        setShowConfirmation(true);

        // Resend confirmation email
        await supabase.auth.resend({
          email: formData.email,
          type: 'signup',
        });

        setIsLoading(false);
        return;
      }

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
                  <FormLabel>{tCommon('emailInputLabel')}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={tCommon('emailInputPlaceholder')}
                      {...field}
                      className="w-full"
                      type="email"
                      disabled={isLoading}
                      autoComplete="section-login username"
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
                      autocomplete="section-login current-password"
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
            <Button
              type="button"
              variant="link"
              className="h-auto p-0 text-bw-50 hover:text-marigold-50 underline"
              disabled={isLoading}
              onClick={() => router.push('?step=reset')}
            >
              {tLogin('forgotPassword')}
            </Button>
          </CardFooter>
        </form>
      </Form>
      {showConfirmation && pendingEmail && (
        <ConfirmationForm initialEmail={pendingEmail} onClose={() => setShowConfirmation(false)} />
      )}
    </Card>
  );
}
