import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { Card, CardContent, CardFooter } from '@/components/ui/Card';
import { useTranslations } from 'next-intl';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/Form';
import { PasswordInput } from './PasswordInput';

interface SignInFormProps {
  onSubmit: (values: { email: string; password: string }) => void;
}

export function SignInForm({ onSubmit }: SignInFormProps) {
  const t = useTranslations('Login.SignInTab');

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

  return (
    <Card className="shadow-none">
      <Form {...signInForm}>
        <form onSubmit={signInForm.handleSubmit(onSubmit)}>
          <CardContent className="space-y-6 p-0">
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
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </CardContent>

          <CardFooter className="flex-col gap-6">
            <Button type="submit" size="full">
              {t('signInButtonLabel')}
            </Button>
            <div className="w-full border-t border-gray-300" />
            <Button size={'full'} variant={'secondary'}>
              <svg
                className="w-5 h-5 mr-2"
                viewBox="0 0 533.5 544.3"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M533.5 278.4c0-17.4-1.6-34.1-4.6-50.4H272v95.3h146.9c-6.3 33.7-25 62.1-53.2 81l86 66.9c50.1-46.2 81.8-114.2 81.8-192.8z"
                  fill="#4285f4"
                />
                <path
                  d="M272 544.3c72.6 0 133.6-24.1 178.2-65.2l-86-66.9c-23.8 16-54.3 25.4-92.2 25.4-70.9 0-131-47.9-152.5-112.1l-89.4 69.4c41.5 82.1 126.7 139.4 241.9 139.4z"
                  fill="#34a853"
                />
                <path
                  d="M119.5 325.5c-10.6-31.5-10.6-65.7 0-97.2l-89.4-69.4c-39.2 76.4-39.2 159.6 0 236z"
                  fill="#fbbc04"
                />
                <path
                  d="M272 107.7c39.5-.6 77.5 13.9 106.4 40.9l79.4-79.4C408.4 24.3 342.3-.3 272 0 156.8 0 71.6 57.3 30.1 139.4l89.4 69.4C141 155.6 201.1 107.7 272 107.7z"
                  fill="#ea4335"
                />
              </svg>
              {t('signInWithGoogleButtonLabel')}
            </Button>
          </CardFooter>
        </form>
      </Form>
    </Card>
  );
}
