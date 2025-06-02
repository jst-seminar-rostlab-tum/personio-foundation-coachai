'use client';

import { SignInForm } from '@/components/common/SignInForm';
import { SignUpForm } from '@/components/common/SignUpForm';
import { Alert, AlertTitle } from '@/components/ui/Alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { SignInCredentials } from '@/interfaces/Api';
import { userProfileApi } from '@/services/Api';
import { AxiosError } from 'axios';
import { AlertCircleIcon } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function LoginPage() {
  const t = useTranslations('Login');
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const onClickSignIn = async (values: SignInCredentials) => {
    try {
      await userProfileApi.signIn(values);
      router.push('/dashboard');
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        if (err.response?.status === 401) {
          setError(t('SignInTab.alertErrorTitle401'));
        } else {
          setError(t('SignInTab.alertErrorTitleGeneric'));
        }
      } else {
        setError(t('SignInTab.alertErrorTitleGeneric'));
      }
      console.error('Sign in failed:', err);
    }
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
        <Alert>
          <AlertCircleIcon />
          <AlertTitle>{error}</AlertTitle>
        </Alert>
      )}
    </div>
  );
}
