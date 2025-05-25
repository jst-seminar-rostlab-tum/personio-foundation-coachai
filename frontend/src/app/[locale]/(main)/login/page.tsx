import { Button } from '@/components/ui/button';
import Input from '@/components/ui/input';
import Label from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { useTranslations } from 'next-intl';

export default function LoginPage() {
  const t = useTranslations('LoginPage');

  return (
    <div>
      <div>{t('welcome')}</div>
      <div>{t('description')}</div>
      <Tabs defaultValue="sign-in" className="w-[400px]">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="sign-in">{t('SignInTab.title')}</TabsTrigger>
          <TabsTrigger value="sign-up">{t('SignUpTab.title')}</TabsTrigger>
        </TabsList>
        <TabsContent value="sign-in">
          <Card>
            <CardContent className="space-y-2">
              <div className="space-y-1">
                <Label htmlFor="email">{t('SignInTab.emailInputLabel')}</Label>
                <Input id="email" placeholder={t('SignInTab.emailInputPlaceholder')} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password">{t('SignInTab.passwordInputLabel')}</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder={t('SignInTab.passwordInputPlaceholder')}
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button>{t('SignInTab.signInButtonLabel')}</Button>
            </CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="sign-up">
          <Card>
            <CardContent className="space-y-2">
              <div className="space-y-1">
                <Label htmlFor="full-name">{t('SignUpTab.fullNameInputLabel')}</Label>
                <Input id="full-name" placeholder={t('SignUpTab.fullNameInputPlaceholder')} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="email">{t('SignUpTab.emailInputLabel')}</Label>
                <Input id="email" placeholder={t('SignUpTab.emailInputPlaceholder')} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="phone-number">{t('SignUpTab.phoneNumberInputLabel')}</Label>
                <Input id="phone-number" placeholder={t('SignUpTab.phoneNumberInputPlaceholder')} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="password">{t('SignUpTab.passwordInputLabel')}</Label>
                <Input id="password" placeholder={t('SignUpTab.passwordInputPlaceholder')} />
              </div>
            </CardContent>
            <CardFooter>
              <Button>{t('SignUpTab.signUpButtonLabel')}</Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
