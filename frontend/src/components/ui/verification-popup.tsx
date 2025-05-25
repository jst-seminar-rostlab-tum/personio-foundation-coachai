import { Button } from '@/components/ui/button';
import Input from '@/components/ui/input';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
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
} from '@/components/ui/form';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { userProfileApi } from '@/services/Api';

interface VerificationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  phoneNumber: string;
  formData?: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  };
}

export function VerificationPopup({
  isOpen,
  onClose,
  phoneNumber,
  formData,
}: VerificationPopupProps) {
  const t = useTranslations('LoginPage');
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verificationSchema = z.object({
    code: z.string().min(1, 'Verification code is required'),
  });

  const form = useForm({
    resolver: zodResolver(verificationSchema),
    mode: 'onTouched',
    defaultValues: {
      code: '',
    },
  });

  //   const handleSubmit = async (values: z.infer<typeof verificationSchema>) => {
  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Verify the code
      //   const isVerified = await userProfileApi.verifyCode(phoneNumber, values.code);
      const isVerified = true;

      if (!isVerified) {
        setError(t('Verification.invalidCode'));
        return;
      }

      // If verification successful and we have form data, create the user
      if (formData) {
        await userProfileApi.create({
          full_name: formData.fullName,
          email: formData.email,
          phone_number: formData.phoneNumber,
          password: formData.password,
        });
      }

      // Close the popup and redirect
      onClose();
      router.push('/');
    } catch (err: unknown) {
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'data' in err.response &&
        err.response.data &&
        typeof err.response.data === 'object' &&
        'detail' in err.response.data
      ) {
        setError(err.response.data.detail as string);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t('Verification.genericError'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <Card className="relative w-[90%] max-w-sm border-0 shadow-lg bg-white animate-in fade-in zoom-in duration-200">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)}>
            <CardContent className="space-y-4 p-4">
              <h2 className="text-xl font-semibold text-center">{t('Verification.title')}</h2>
              <p className="text-sm text-center text-gray-600">
                {t('Verification.description', { phoneNumber })}
              </p>

              {error && (
                <div className="p-2 text-sm text-red-500 bg-red-50 rounded-md">{error}</div>
              )}

              <FormField
                control={form.control}
                name="code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm">{t('Verification.codeLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('Verification.codePlaceholder')}
                        {...field}
                        className="w-full"
                        disabled={isLoading}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter className="flex-col gap-2 p-4">
              <Button size={'full'} type="submit" disabled={isLoading}>
                {isLoading ? t('Verification.verifyingButton') : t('Verification.verifyButton')}
              </Button>
              <Button size={'full'} variant={'secondary'} onClick={onClose} disabled={isLoading}>
                {t('Verification.cancelButton')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
    </div>
  );
}
