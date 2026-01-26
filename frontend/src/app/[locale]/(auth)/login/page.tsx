import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import LoginPageComponent from './components/LoginPage';
import UpdatePasswordForm from './components/UpdatePasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';

/**
 * Generates localized metadata for the login page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '/login', true);
}

/**
 * Props for the login page, including auth step query parameters.
 */
interface LoginPageProps {
  searchParams: Promise<{ step?: string }>;
}

/**
 * Renders the login page and switches between auth flow steps.
 */
export default async function LoginPage({ searchParams }: LoginPageProps) {
  const { step } = searchParams ? await searchParams : {};
  const currentStep = step ?? 'login';

  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <LoginPageComponent />

        {currentStep === 'reset' && <ResetPasswordForm />}

        {currentStep === 'update-password' && <UpdatePasswordForm />}
      </div>
    </div>
  );
}
