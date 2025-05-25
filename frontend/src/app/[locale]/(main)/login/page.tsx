'use client';

import { Button } from '@/components/ui/button';
import Input from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Checkbox from '@/components/ui/checkbox';
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

export default function LoginPage() {
  const t = useTranslations('LoginPage');

  const signInFormSchema = z.object({
    email: z.string().min(1, t('SignInTab.emailInputError')),
    password: z.string().min(1, t('SignInTab.passwordInputError')),
  });

  const signInForm = useForm({
    resolver: zodResolver(signInFormSchema),
    mode: 'onTouched',
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onClickSignIn = (values) => {
    console.warn(values);
  };

  const signUpFormSchema = z.object({
    fullName: z.string().min(1, t('SignUpTab.fullNameInputError')),
    email: z.string().min(1, t('SignUpTab.emailInputError')),
    phoneNumber: z.string().min(1, t('SignUpTab.phoneNumberInputError')),
    password: z.string().min(1, t('SignUpTab.passwordInputError')),
    terms: z.literal(true),
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

  const onClickSignUp = (values) => {
    console.warn(values);
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
                <Card className="shadow-none">
                  <Form {...signInForm}>
                    <form onSubmit={signInForm.handleSubmit(onClickSignIn)}>
                      <CardContent className="space-y-6 p-0">
                        <FormField
                          control={signInForm.control}
                          name="email"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>{t('SignInTab.emailInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder={t('SignInTab.emailInputPlaceholder')}
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
                              <FormLabel>{t('SignInTab.passwordInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  type="password"
                                  placeholder={t('SignInTab.passwordInputPlaceholder')}
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
                          {t('SignInTab.signInButtonLabel')}
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
                          {t('SignInTab.signInWithGoogleButtonLabel')}
                        </Button>
                      </CardFooter>
                    </form>
                  </Form>
                </Card>
              </TabsContent>

              <TabsContent value="sign-up" className="mt-0">
                <Card className="border-0 shadow-none">
                  <Form {...signUpForm}>
                    <form onSubmit={signUpForm.handleSubmit(onClickSignUp)}>
                      <CardContent className="space-y-6 p-0">
                        <FormField
                          control={signUpForm.control}
                          name="fullName"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>{t('SignUpTab.fullNameInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder={t('SignUpTab.fullNameInputPlaceholder')}
                                  {...field}
                                  className="w-full"
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
                              <FormLabel>{t('SignUpTab.emailInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder={t('SignUpTab.emailInputPlaceholder')}
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
                          control={signUpForm.control}
                          name="phoneNumber"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>{t('SignUpTab.phoneNumberInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder={t('SignUpTab.phoneNumberInputPlaceholder')}
                                  {...field}
                                  className="w-full"
                                  type="tel"
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
                              <FormLabel>{t('SignUpTab.passwordInputLabel')}</FormLabel>
                              <FormControl>
                                <Input
                                  placeholder={t('SignUpTab.passwordInputPlaceholder')}
                                  {...field}
                                  className="w-full"
                                  type="password"
                                />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />

                        <Card className="shadow-none border border-bw-30 p-2">
                          <CardContent className="p-1">
                            <p className="text-base">
                              We strictly adhere to GDPR by collecting only essential data, storing
                              nothing unnecessary, and deleting data as soon as possible.{' '}
                              <Button
                                variant="link"
                                className="h-auto p-0 text-blue-600 hover:text-blue-800 underline"
                              >
                                read more
                              </Button>
                            </p>
                          </CardContent>
                        </Card>

                        <FormField
                          control={signUpForm.control}
                          name="terms"
                          render={({ field }) => (
                            <FormItem className="flex items-center space-x-2">
                              <FormControl>
                                <Checkbox
                                  className=""
                                  checked={field.value}
                                  onClick={() => field.onChange(!field.value)}
                                />
                              </FormControl>
                              <FormLabel>{t('SignUpTab.agreeToTermsCheckboxLabel')}</FormLabel>
                            </FormItem>
                          )}
                        />
                      </CardContent>
                      <CardFooter className="flex-col gap-6">
                        <Button size={'full'} type="submit">
                          {t('SignUpTab.signUpButtonLabel')}
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
                          {t('SignUpTab.signUpWithGoogleButtonLabel')}
                        </Button>
                      </CardFooter>
                    </form>
                  </Form>
                </Card>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
