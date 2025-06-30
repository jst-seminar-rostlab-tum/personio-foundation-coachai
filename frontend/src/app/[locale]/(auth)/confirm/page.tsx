import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import { Metadata } from 'next';
import ConfirmationForm from './components/ConfirmationForm';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/confirm', true);
}

export default function ConfirmPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <ConfirmationForm />
      </div>
    </div>
  );
}
