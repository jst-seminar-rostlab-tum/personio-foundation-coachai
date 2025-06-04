import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/MetadataProps';
import AboutFooter from '@/components/layout/AboutFooter';

export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/privacy', true);
}

export default function PrivacyPage() {
  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8 p-8">
        <h1 className="text-4xl font-semibold">Privacy Policy</h1>
        <h2 className="text-xl font-semibold">Data Collection</h2>
        <p className="text-base leading-loose">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer a leo in ligula sagittis
          varius at ut neque. Nulla finibus mi eu malesuada eleifend. Ut ac turpis a risus viverra
          sagittis sed vitae massa. Vestibulum tempus, mauris a elementum maximus, quam dolor
          venenatis magna, ac sollicitudin leo nisi vel nulla. Phasellus ac libero erat. Fusce ante
          lectus, varius vitae purus non, vulputate viverra ipsum. Aliquam rhoncus leo eget dictum
          vestibulum. Aliquam quis vestibulum lacus. Curabitur quis egestas mi. Vivamus pharetra,
          leo vitae congue congue, odio quam commodo lectus, sed hendrerit ex tortor eget neque. Sed
          auctor suscipit ullamcorper. Ut facilisis, augue ut lobortis vehicula, nisi nunc accumsan
          neque, ut pharetra odio quam a enim. Donec convallis viverra sapien a dictum. Etiam
          malesuada massa quis nisi aliquam placerat.
        </p>
      </section>
      <AboutFooter />
    </div>
  );
}
