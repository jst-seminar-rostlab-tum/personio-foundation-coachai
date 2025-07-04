import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import { Metadata } from 'next';
import UpdatePasswordForm from './components/UpdatePasswordForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/update-password', true);
}

export default function UpdatePasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <UpdatePasswordForm />
      </div>
    </div>
  );
}
