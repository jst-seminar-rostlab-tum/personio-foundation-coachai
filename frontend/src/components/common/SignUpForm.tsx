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
import Checkbox from '@/components/ui/Checkbox';
import { useState } from 'react';
import { userProfileApi } from '@/services/Api';
import { SignUpFormProps } from '@/interfaces/SignUpForm';
import { PasswordRequirement } from '@/interfaces/PasswordInput';
import { PasswordInput } from './PasswordInput';
import PrivacyDialog from './PrivacyDialog';
import { VerificationPopup } from './VerificationPopup';

export function SignUpForm({ onSubmit }: SignUpFormProps) {
  const t = useTranslations('Login.SignUpTab');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showVerification, setShowVerification] = useState(false);
  const [showPrivacyDialog, setShowPrivacyDialog] = useState(false);
  const [signedUpPhone, setSignedUpPhone] = useState('');

  const signUpFormSchema = z.object({
    fullName: z.string().min(1, t('fullNameInputError')),
    email: z.string().email(t('emailInputError')),
    phoneNumber: z.string().regex(/^\+[1-9]\d{7,14}$/, t('phoneNumberInputError')),
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
      phoneNumber: '',
      password: '',
      terms: false,
    },
  });

  const passwordRequirements: PasswordRequirement[] = [
    {
      id: 'length',
      label: t('passwordInputRequirementOneLabel'),
      test: (password: string) => password.length >= 8,
    },
    {
      id: 'uppercase',
      label: t('passwordInputRequirementTwoLabel'),
      test: (password: string) => /[A-Z]/.test(password),
    },
    {
      id: 'special',
      label: t('passwordInputRequirementThreeLabel'),
      test: (password: string) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password),
    },
  ];

  const handleSubmit = async (values: z.infer<typeof signUpFormSchema>) => {
    // Clear any existing errors at the start of a new submission
    setError(null);

    try {
      setIsLoading(true);

      // First validate the user data
      const validationResponse = await userProfileApi.validate({
        full_name: values.fullName,
        email: values.email,
        phone_number: values.phoneNumber,
        password: values.password,
        preferred_language: 'en', // Default language
        preferred_learning_style_id: '',
        preferred_session_length: '',
      });

      if (!validationResponse.is_valid && validationResponse.errors) {
        // Set field-specific errors
        Object.entries(validationResponse.errors).forEach(([field, message]) => {
          const errorMessage = String(message);
          switch (field) {
            case 'email':
              signUpForm.setError('email', { message: errorMessage });
              break;
            case 'phone_number':
              signUpForm.setError('phoneNumber', { message: errorMessage });
              break;
            case 'full_name':
              signUpForm.setError('fullName', { message: errorMessage });
              break;
            default:
              setError(errorMessage);
          }
        });
        return;
      }

      // If validation passes, show verification popup
      setSignedUpPhone(values.phoneNumber);
      setShowVerification(true);

      // Call the parent onSubmit handler with the form data
      onSubmit({
        fullName: values.fullName,
        email: values.email,
        phoneNumber: values.phoneNumber,
        password: values.password,
        terms: values.terms,
      });
    } catch (err: unknown) {
      let errorMessage = t('genericError');

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
        const { detail } = err.response.data;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail[0]?.msg || t('genericError');
        } else if (typeof detail === 'object' && detail !== null && 'msg' in detail) {
          errorMessage = String(detail.msg);
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Card className="border-0 shadow-none">
        <Form {...signUpForm}>
          <form onSubmit={signUpForm.handleSubmit(handleSubmit)}>
            <CardContent className="space-y-6 p-0">
              {error && (
                <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">{error}</div>
              )}

              <FormField
                control={signUpForm.control}
                name="fullName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('fullNameInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('fullNameInputPlaceholder')}
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
                control={signUpForm.control}
                name="phoneNumber"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t('phoneNumberInputLabel')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('phoneNumberInputPlaceholder')}
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
                    <FormLabel>{t('passwordInputLabel')}</FormLabel>
                    <FormControl>
                      <PasswordInput
                        placeholder={t('passwordInputPlaceholder')}
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
                    {t('gdprAdherenceText')}
                    <Button
                      variant="ghost"
                      type="button"
                      className="h-auto p-0 text-blue-600 hover:text-blue-800 underline"
                      onClick={() => setShowPrivacyDialog(true)}
                    >
                      {t('readMoreOnGdprLink')}
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
                      <FormLabel>{t('agreeToTermsCheckboxLabel')}</FormLabel>
                    </div>
                  </FormItem>
                )}
              />
            </CardContent>
            <CardFooter className="flex-col gap-6">
              <Button size="full" type="submit" disabled={isLoading}>
                {t('signUpButtonLabel')}
              </Button>
              <div className="w-full border-t border-gray-300" />
              <Button size="full" variant="secondary" disabled={isLoading}>
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
                {t('signUpWithGoogleButtonLabel')}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>

      <VerificationPopup
        isOpen={showVerification}
        onClose={() => setShowVerification(false)}
        recipientPhoneNumber={signedUpPhone}
        formData={signUpForm.getValues()}
      />

      <PrivacyDialog open={showPrivacyDialog} onOpenChange={setShowPrivacyDialog}></PrivacyDialog>
    </>
  );
}
