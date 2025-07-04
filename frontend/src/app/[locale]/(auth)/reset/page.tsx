import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { Metadata } from 'next';
import ResetPasswordForm from './components/ResetPasswordForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/reset', true);
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <ResetPasswordForm />
      </div>
    </div>
  );
}
