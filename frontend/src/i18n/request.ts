import { getRequestConfig } from 'next-intl/server';
import { hasLocale } from 'next-intl';
import routing from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  const requested = await requestLocale;
  const locale = hasLocale(routing.locales, requested) ? requested : routing.defaultLocale;
  const messages = {
    Confirm: (await import(`../../messages/${locale}/Confirm.json`)).default,
    Common: (await import(`../../messages/${locale}/Common.json`)).default,
    HomePage: (await import(`../../messages/${locale}/HomePage.json`)).default,
    ConversationScenario: (await import(`../../messages/${locale}/ConversationScenario.json`))
      .default,
    Admin: (await import(`../../messages/${locale}/Admin.json`)).default,
    Dashboard: (await import(`../../messages/${locale}/Dashboard.json`)).default,
    Feedback: (await import(`../../messages/${locale}/Feedback.json`)).default,
    History: (await import(`../../messages/${locale}/History.json`)).default,
    Login: (await import(`../../messages/${locale}/Login.json`)).default,
    Onboarding: (await import(`../../messages/${locale}/Onboarding.json`)).default,
    Preparation: (await import(`../../messages/${locale}/Preparation.json`)).default,
    Simulation: (await import(`../../messages/${locale}/Simulation.json`)).default,
    TrainingSettings: (await import(`../../messages/${locale}/TrainingSettings.json`)).default,
    AppHeader: (await import(`../../messages/${locale}/AppHeader.json`)).default,
    PrivacyPolicy: (await import(`../../messages/${locale}/PrivacyPolicy.json`)).default,
    TermsOfService: (await import(`../../messages/${locale}/TermsOfService.json`)).default,
    PersonalizationOptions: (await import(`../../messages/${locale}/PersonalizationOptions.json`))
      .default,
  };

  return {
    locale,
    messages,
  };
});
