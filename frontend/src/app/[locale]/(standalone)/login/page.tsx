'use client';

import { SignInForm } from '@/components/common/SignInForm';
import { SignUpForm } from '@/components/common/SignUpForm';
import { Alert, AlertTitle } from '@/components/ui/Alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { SignInCredentials } from '@/interfaces/SignInForm';
import { AlertCircleIcon } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useState } from 'react';

export default function LoginPage() {
  const t = useTranslations('Login');
  const [error, setError] = useState<string | null>(null);

  const onClickSignIn = async (values: SignInCredentials) => {
    console.warn('LoginPage: onClickSignIn called with values:', values);
    // TODO: Call sign-in API
  };

  const onClickSignUp = () => {};

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
                <SignUpForm onSubmit={onClickSignUp} setError={setError} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
      {error && (
        <Alert variant="destructive">
          <AlertCircleIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      )}
    </div>
  );
}
