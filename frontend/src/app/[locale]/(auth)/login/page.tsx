import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import LoginPageComponent from './components/LoginPage';
import ConfirmationForm from './components/ConfirmationForm';
import UpdatePasswordForm from './components/UpdatePasswordForm';
import ResetPasswordForm from './components/ResetPasswordForm';
import { ModalWrapper } from './components/ModelWrapper';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;

  return generateDynamicMetadata(locale, '/login', true);
}

interface LoginPageProps {
  searchParams: Promise<{ step?: string }>;
}
export default async function LoginPage({ searchParams }: LoginPageProps) {
  const { step } = searchParams ? await searchParams : {};
  const currentStep = step ?? 'login';

  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <LoginPageComponent />

        {currentStep === 'confirm' && (
          <ModalWrapper>
            <ConfirmationForm />
          </ModalWrapper>
        )}

        {currentStep === 'reset' && (
          <ModalWrapper>
            <ResetPasswordForm />
          </ModalWrapper>
        )}

        {currentStep === 'update-password' && (
          <ModalWrapper>
            <UpdatePasswordForm />
          </ModalWrapper>
        )}
      </div>
    </div>
  );
}
