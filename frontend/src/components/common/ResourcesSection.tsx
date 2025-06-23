import { useTranslations } from 'next-intl';
import ResourceItem from './ResourceItem';

const resources = [
  {
    name: 'Giving Feedback (CC BY-NC 4.0)',
    author: 'Personio Foundation',
    fileUrl: '/resources/giving-feedback.pdf',
  },
  {
    name: 'Effective Communication',
    author: 'Jane Doe',
    fileUrl: '/resources/effective-communication.pdf',
  },
];

export default function ResourcesSection() {
  const t = useTranslations('Common');
  return (
    <section className="flex flex-col gap-4 mt-8 w-full">
      <div>
        <h2 className="text-xl">{t('resources.title')}</h2>
        <p className="text-base text-bw-40">{t('resources.subtitle')}</p>
      </div>
      <div className="flex flex-col gap-4">
        {resources.map((resource) => (
          <ResourceItem
            key={resource.name}
            name={resource.name}
            author={resource.author}
            fileUrl={resource.fileUrl}
          />
        ))}
      </div>
    </section>
  );
}
