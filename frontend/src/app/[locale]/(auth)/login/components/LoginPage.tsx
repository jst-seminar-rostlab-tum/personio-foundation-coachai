import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { getTranslations } from 'next-intl/server';
import { HighlightedAppName } from '@/components/common/HighlightedAppName';
import { SignInForm } from './SignInForm';
import { SignUpForm } from './SignUpForm';

export default async function LoginPageComponent() {
  const t = await getTranslations('Login');
  return (
    <Card>
      <CardHeader className="mt-5">
        <CardTitle>
          {t('welcome')} <HighlightedAppName />
        </CardTitle>
        <CardDescription>{t('description')}</CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="sign-in" className="mt-5">
          <TabsList>
            <TabsTrigger value="sign-in">{t('signIn')}</TabsTrigger>
            <TabsTrigger value="sign-up">{t('signUp')}</TabsTrigger>
          </TabsList>

          <TabsContent value="sign-in">
            <SignInForm />
          </TabsContent>

          <TabsContent value="sign-up" className="mt-0">
            <SignUpForm />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
