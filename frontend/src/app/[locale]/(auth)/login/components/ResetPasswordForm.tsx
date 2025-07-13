'use client';

import { Button } from '@/components/ui/Button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/Form';
import Input from '@/components/ui/Input';
import { createClient } from '@/lib/supabase/client';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslations } from 'next-intl';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import z from 'zod';

export default function ResetPasswordForm() {
  const t = useTranslations('Reset');
  const tCommon = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>();

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const passwordResetFormSchema = z.object({
    email: z.string().email(tCommon('emailInputError')),
  });

  const form = useForm({
    resolver: zodResolver(passwordResetFormSchema),
    mode: 'onTouched',
    defaultValues: {
      email: useSearchParams().get('email') ?? '',
    },
  });

  const sendPasswordReset = async (values: z.infer<typeof passwordResetFormSchema>) => {
    setError(null);
    setIsLoading(true);

    try {
      const supabase = await createClient();
      const { error: supabaseError } = await supabase.auth.resetPasswordForEmail(values.email, {
        redirectTo: `${window.location.origin}/update-password`,
      });
      if (supabaseError) {
        setError(supabaseError.message || tCommon('unknownError'));
        return;
      }
      showSuccessToast(t('successMessage'));

      form.reset();
    } catch (err) {
      console.error('Error sending password reset:', err);
      setError(tCommon('unknownError'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <Card className="relative w-[90%] max-w-sm border-0 bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(sendPasswordReset)}>
            <CardHeader>
              <CardTitle>{t('title')}</CardTitle>
              <CardDescription>{t('description')}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4 p-4">
              <FormField
                control={form.control}
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

              <FormMessage />
            </CardContent>

            <CardFooter className="flex-col gap-2 p-4">
              <Button type="submit" size="full" disabled={isLoading}>
                {t('sendResetEmailButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
