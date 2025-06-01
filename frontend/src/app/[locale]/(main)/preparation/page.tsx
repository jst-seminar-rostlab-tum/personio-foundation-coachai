import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import { ArrowLeftIcon, Play } from 'lucide-react';
import Link from 'next/link';
import { UserOption } from '@/interfaces/UserInputFields';
import PreparationChecklist from '@/components/common/PreparationChecklist';
import ObjectivesList from '@/components/common/ObjectivesList';
import { Button } from '@/components/ui/Button';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/preparation', true);
}

export default function PreparationPage() {
  const objectives: UserOption[] = [
    { id: 'o1', label: 'Clearly communicate the impact of the missed deadlines' },
    { id: 'o2', label: 'Understand potential underlying causes' },
    { id: 'o3', label: 'Collaboratively develop a solution' },
    { id: 'o4', label: 'End the conversation on a positive note' },
  ];

  const preparationItems: UserOption[] = [
    { id: 'p1', label: 'Gather specific examples of missed deadlines' },
    { id: 'p2', label: 'Document the impact on team and projects' },
    { id: 'p3', label: 'Consider potential underlying causes' },
    { id: 'p4', label: 'Prepare open-ended questions' },
    { id: 'p5', label: 'Think about potential solutions to suggest' },
    { id: 'p6', label: 'Plan a positive closing statement' },
    { id: 'p7', label: 'Choose a comfortable meeting environment' },
  ];

  return (
    <div className="flex flex-col gap-8 p-8">
      <h1 className="text-2xl text-center">Check Your Training Setup</h1>

      <section className="flex flex-col gap-4">
        <div className="flex flex-col gap-4 border border-marigold-30 rounded-lg p-8">
          <h2 className="text-xl">Giving Constructive Feedback</h2>
          <div className="text-base text-bw-70 italic leading-loose">
            You need to talk to Sarah, a team member who has missed several deadlines recently,
            affecting morale and timelines. Your goal is to address it constructively while keeping
            a positive relationship.
          </div>
        </div>
      </section>

      <div className="flex flex-col md:flex-row gap-4 items-stretch">
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">Objectives</h2>
          </div>
          <ObjectivesList items={objectives} />
        </section>

        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">Preparation Checklist</h2>
          </div>
          <PreparationChecklist items={preparationItems} />
        </section>
      </div>

      <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
        <h2 className="text-xl">Resources</h2>
      </section>

      <div className="flex gap-4">
        <Link href="/new-training" className="flex-1">
          <Button size="full" variant="outline">
            <ArrowLeftIcon />
            Go Back
          </Button>
        </Link>

        <Link href="/simulation/1" className="flex-1">
          <Button size="full">
            <Play />
            Start Training
          </Button>
        </Link>
      </div>
    </div>
  );
}
