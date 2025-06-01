import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';
import { ArrowLeftIcon, Play } from 'lucide-react';
import Link from 'next/link';
import PreparationChecklist from '@/components/common/PreparationChecklist';
import ObjectivesList from '@/components/common/ObjectivesList';
import { Button } from '@/components/ui/Button';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/preparation', true);
}

export default function PreparationPage() {
  const mockData = {
    id: 'f65e1b1b-1234-4a5b-9876-abc123def456',
    case_id: '9f27e05e-4321-4d89-b123-cde456gh7890',
    objectives: [
      'Clearly communicate the impact of the missed deadlines',
      'Understand potential underlying causes',
      'Collaboratively develop a solution',
      'End the conversation on a positive note',
    ],
    key_concepts: [
      { header: 'Time management', value: 'Time management' },
      { header: 'Collaboration', value: 'Collaboration' },
    ],
    prep_checklist: [
      'Gather specific examples of missed deadlines',
      'Document the impact on team and projects',
      'Consider potential underlying causes',
      'Prepare open-ended questions',
      'Think about potential solutions to suggest',
      'Plan a positive closing statement',
      'Choose a private, comfortable meeting environment',
    ],
  };

  return (
    <div className="flex flex-col gap-8 p-8">
      <h1 className="text-2xl text-center">Check Your Training Setup</h1>

      <section className="flex flex-col gap-4 bg-marigold-5 border border-marigold-30 rounded-lg p-8 text-marigold-95">
        <h2 className="text-xl">Giving Constructive Feedback</h2>
        <div className="text-base italic leading-loose">
          You need to talk to Sarah, a team member who has missed several deadlines recently,
          affecting morale and timelines. Your goal is to address it constructively while keeping a
          positive relationship.
        </div>
      </section>

      <div className="flex flex-col md:flex-row gap-4 items-stretch">
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">Objectives</h2>
          </div>
          <ObjectivesList objectives={mockData.objectives} />
        </section>

        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="flex items-center gap-2">
            <h2 className="text-xl">Preparation Checklist</h2>
          </div>
          <PreparationChecklist checklist={mockData.prep_checklist} />
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
