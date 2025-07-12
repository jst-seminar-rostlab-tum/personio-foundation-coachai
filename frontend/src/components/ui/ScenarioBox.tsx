import React from 'react';
import { useTranslations } from 'next-intl';
import { Badge } from './Badge';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from './Accordion';
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
  return <span className="text-md font-semibold">{t('personaProfileHeader')}</span>;
}

const ScenarioBox: React.FC<ScenarioBoxProps> = ({
  header,
  description,
  difficulty,
  personalizationItems,
}) => (
  <div className="flex flex-col gap-12 w-full border border-bw-20 rounded-lg p-8 text-bw-70">
    <div className="flex items-center justify-between w-full mb-4">
      <div className="text-xl font-semibold">{header}</div>
      <Badge difficulty={difficulty}>
        {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
      </Badge>
    </div>
    <span className="text-base italic leading-loose">{description}</span>
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

export default ScenarioBox;
