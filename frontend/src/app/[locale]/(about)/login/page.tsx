import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import { SignInForm } from '@/app/[locale]/(about)/login/components/SignInForm';
import { SignUpForm } from '@/app/[locale]/(about)/login/components/SignUpForm';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { useTranslations } from 'next-intl';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/login', true);
}

export default function LoginPage() {
  const t = useTranslations('Login');

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
                <SignInForm />
              </TabsContent>

              <TabsContent value="sign-up" className="mt-0">
                <SignUpForm />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
