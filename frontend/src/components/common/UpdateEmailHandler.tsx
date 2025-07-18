'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { createClient } from '@/lib/supabase/client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import z from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/Dialog';
import { Card, CardContent, CardFooter } from '../ui/Card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '../ui/Form';
import Input from '../ui/Input';
import { Button } from '../ui/Button';

interface UpdateEmailHandlerProps {
  id?: string;
  children: React.ReactNode;
}

export function UpdateEmailHandler({ children }: UpdateEmailHandlerProps) {
  const [isLoading, setLoading] = useState(false);
  const t = useTranslations('Settings');
  const tCommon = useTranslations('Common');

  const updateEmailFormSchema = z.object({
    email: z.string().email(tCommon('emailInputError')),
  });

  const form = useForm({
    resolver: zodResolver(updateEmailFormSchema),
    mode: 'onTouched',
    defaultValues: {
      email: '',
    },
  });

  async function updateEmail(values: z.infer<typeof updateEmailFormSchema>) {
    setLoading(true);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser(
        {
          email: values.email,
        },
        {
          emailRedirectTo: `${window.location.origin}/api/auth/email-change-redirect`,
        }
      );
      if (error) {
        switch (error.code) {
          case 'email_exists':
            showErrorToast(error, t('emailExistsError'));
            break;
          case 'over_email_send_rate_limit':
            showErrorToast(error, t('overEmailSendRateLimitError'));
            break;
          default:
            showErrorToast(error, t('updateEmailError'));
        }
      } else {
        showSuccessToast(t('updateEmailSuccess'));
      }
    } catch (error) {
      showErrorToast(error, t('updateEmailError'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-2xl">{t('updateEmailTitle')}</DialogTitle>
          <DialogDescription className="text-bw-40 text-base">
            {t('updateEmailDescription')}
          </DialogDescription>
        </DialogHeader>

        <Card>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(updateEmail)}>
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
                  {t('updateEmailButtonLabel')}
                </Button>
              </CardFooter>
            </form>
          </Form>
        </Card>
      </DialogContent>
    </Dialog>
  );
}
