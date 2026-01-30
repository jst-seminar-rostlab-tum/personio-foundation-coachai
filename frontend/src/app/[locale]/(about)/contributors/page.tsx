import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { MetadataProps } from '@/interfaces/props/MetadataProps';
import { getTranslations } from 'next-intl/server';
import { Monitor, Server, Settings, Calendar, UserCheck } from 'lucide-react';

/**
 * Generates localized metadata for the contributors page.
 */
export async function generateMetadata({ params }: MetadataProps): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/contributors', false);
}

/**
 * Lists contributor teams and members for the project.
 */
export default async function ContributorsPage() {
  const t = await getTranslations('Contributors');
  const tCommon = await getTranslations('Common');

  const teams = [
    {
      title: t('projectLead'),
      members: ['Tim Alexander Meyerhoff'],
      icon: UserCheck,
    },
    {
      title: 'Frontend',
      members: [
        'Feres Essafi',
        'Sam Miao',
        'Teodora Petrova',
        'Vishavjeet Ghotra',
        `Yulius Seliman (${t('teamLead')})`,
      ],
      icon: Monitor,
    },
    {
      title: 'Backend',
      members: [
        'Anna Schleich',
        'Omar Elfatairy',
        `Ron Autenrieb (${t('teamLead')})`,
        'Xiyu Zhang',
        'Zeyu Li',
      ],
      icon: Server,
    },
    {
      title: 'Meta',
      members: [
        'Adam Gdoura',
        'Aleksandra Topalova',
        'Christopher Lyko',
        `Simon Paul (${t('teamLead')})`,
        'Stefan Dimitrov',
      ],
      icon: Settings,
    },
    {
      title: t('programManagement'),
      members: ['Amin Ben Saad', 'Haochun Ma', 'Lachezar Marinov'],
      icon: Calendar,
    },
  ];

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8 py-8 md:py-20">
        <div className="container">
          <h1 className="text-4xl font-semibold break-words mb-12">{tCommon('contributors')}</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {teams.map((team) => (
              <div
                key={team.title}
                className="p-6 rounded-xl shadow-sm border border-gray-100 bg-custom-beige"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-forest-90 flex items-center justify-center text-white">
                    <team.icon className="h-5 w-5" />
                  </div>
                  <h2 className="text-xl font-semibold text-black">{team.title}</h2>
                </div>
                <ul className="space-y-2">
                  {team.members.map((member) => (
                    <li key={member} className="text-black/80">
                      {member}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
