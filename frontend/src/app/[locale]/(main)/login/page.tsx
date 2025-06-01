'use client';

import { SignInForm } from '@/components/common/SignInForm';
import { SignUpForm } from '@/components/common/SignUpForm';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const t = useTranslations('Login');
  const router = useRouter();

  const onClickSignIn = (values: { email: string; password: string }) => {
    // The actual sign-in logic is handled in the SignInForm component
    // This function is called only after successful sign-in
    console.warn('Sign in successful:', values);
    router.push('/dashboard');
  };

  const onClickSignUp = (values: {
    fullName: string;
    email: string;
    phoneNumber: string;
    password: string;
    terms: boolean;
  }) => {
    console.warn('Sign up successful:', values);
    // The actual sign-up logic is now handled in the SignUpForm component
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="mt-5">
            <CardTitle>{t('welcome')}</CardTitle>
            <CardDescription>{t('description')}</CardDescription>
          </CardHeader>

          <CardContent>
            <Tabs defaultValue="sign-in" className="mt-5">
              <TabsList>
                <TabsTrigger value="sign-in">{t('SignInTab.title')}</TabsTrigger>
                <TabsTrigger value="sign-up">{t('SignUpTab.title')}</TabsTrigger>
              </TabsList>

              <TabsContent value="sign-in">
                <SignInForm onSubmit={onClickSignIn} />
              </TabsContent>

              <TabsContent value="sign-up" className="mt-0">
                <SignUpForm onSubmit={onClickSignUp} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
