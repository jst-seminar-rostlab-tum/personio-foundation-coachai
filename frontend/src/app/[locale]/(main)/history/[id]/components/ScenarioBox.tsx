import React from 'react';
import { useTranslations } from 'next-intl';
import { Badge } from '@/components/ui/Badge';
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '@/components/ui/Accordion';
import Image from 'next/image';
import PersonalizationGroup from './PersonalizationGroup';

interface PersonalizationItem {
  title: string;
  description: string;
}

interface ScenarioBoxProps {
  header: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  personalizationItems: PersonalizationItem[];
}

function PersonaProfileAccordionTrigger() {
  const t = useTranslations('PersonalizationOptions');
  return <span className="text-md font-bold">{t('personaProfileHeader')}</span>;
}

const ScenarioBox: React.FC<ScenarioBoxProps> = ({
  header,
  description,
  difficulty,
  personalizationItems,
}) => {
  const t = useTranslations('PersonalizationOptions');
  return (
    <div className="flex flex-col gap-12 w-full border border-bw-20 rounded-lg p-8 text-bw-70">
      <div className="flex items-center justify-between w-full">
        <div className="text-xl font-semibold">{header}</div>
      </div>
      <span className="text-base italic leading-loose">{description}</span>
      <div className="grid grid-cols-2 w-full gap-16 gap-y-1 px-2 text-bw-70">
        <div className="text-md font-bold mb-2 pl-8">{t('otherPartyLabel')}</div>
        <div className="text-md font-bold mb-2 pl-8">{t('difficultyLabel')}</div>
        <div className="flex items-center gap-4 min-h-[56px] pl-8">
          <Image
            src="/images/personas/persona-angry.png"
            alt="Angry Alex"
            width={56}
            height={56}
            className="rounded-full bg-white border border-bw-10"
          />
          <span className="text-xl font-medium">Angry Alex</span>
        </div>
        <div className="flex items-center min-h-[56px] pl-8">
          <Badge difficulty={difficulty} className="text-xl px-4 py-1">
            {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
          </Badge>
        </div>
      </div>
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="personalization">
          <AccordionTrigger>
            <PersonaProfileAccordionTrigger />
          </AccordionTrigger>
          <AccordionContent>
            <PersonalizationGroup items={personalizationItems} />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default ScenarioBox;
