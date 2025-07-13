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
import { showErrorToast } from '@/lib/utils/toast';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslations } from 'next-intl';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import z from 'zod';

export default function UpdatePasswordForm() {
  const t = useTranslations('Login.UpdatePassword');
  const tCommon = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>();

  const router = useRouter();

  useEffect(() => {
    if (error) {
      showErrorToast(null, error);
    }
  }, [error]);

  const updatePasswordFormSchema = z
    .object({
      code: z.string().nonempty(t('codeInputError')),
      password: z
        .string()
        .min(8, t('passwordLengthError'))
        .regex(/[A-Z]/, t('passwordUppercaseError'))
        .regex(/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/, t('passwordSpecialCharError'))
        .trim(),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t('passwordsMustMatchError'),
      path: ['confirmPassword'],
    });

  const form = useForm({
    resolver: zodResolver(updatePasswordFormSchema),
    mode: 'onChange',
    defaultValues: {
      code: useSearchParams().get('code') ?? '',
    },
  });

  const updatePassword = async (values: z.infer<typeof updatePasswordFormSchema>) => {
    setError(null);
    setIsLoading(true);
    try {
      const supabase = await createClient();
      const { error: supabaseError } = await supabase.auth.updateUser({
        password: values.password,
      });

      if (supabaseError) {
        setError(supabaseError.message || tCommon('unknownError'));
        return;
      }

      router.push('/dashboard');
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
          <form onSubmit={form.handleSubmit(updatePassword)}>
            <CardHeader>
              <CardTitle>{t('title')}</CardTitle>
              <CardDescription>{t('description')}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4 p-4">
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('passwordInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('passwordInputPlaceholder')}
                        {...field}
                        className="w-full"
                        type="password"
                        disabled={isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="confirmPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('confirmPasswordInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('confirmPasswordInputPlaceholder')}
                        {...field}
                        className="w-full"
                        type="password"
                        disabled={isLoading}
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
                {t('updatePasswordButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
