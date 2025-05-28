'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { useTranslations } from 'next-intl';
import { SignInForm } from '@/components/common/SignInForm';
import { SignUpForm } from '@/components/common/SignUpForm';

export default function LoginPage() {
  const t = useTranslations('LoginPage');

  const onClickSignIn = (values: { email: string; password: string }) => {
    console.warn(values);
    // TODO: Implement sign in logic
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
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="text-center pb-6 pt-8">
            <h1 className="text-2xl mb-2">{t('welcome')}</h1>
            <p className="text-bw-40 text-lg">{t('description')}</p>
          </CardHeader>

          <CardContent>
            <Tabs defaultValue="sign-in">
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
