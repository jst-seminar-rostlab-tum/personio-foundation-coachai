import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { SignInFormProps } from '@/interfaces/SignInForm';
import Image from 'next/image';
import GoogleIcon from '@/../public/icons/google-icon.svg';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/Form';
import { PasswordInput } from './PasswordInput';

export function SignInForm({ onSubmit }: SignInFormProps) {
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

  const handleSubmit = async (values: z.infer<typeof signInFormSchema>) => {
    setError(null);
    setIsLoading(true);
    await onSubmit(values);
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
                      className="w-full"
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
              <Image src={GoogleIcon} alt="" className="w-5 h-5 mr-2"></Image>
              {t('signInWithGoogleButtonLabel')}
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
