'use client';

import { useTranslations } from 'next-intl';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';

interface PreparationCollapsibleSectionProps {
  situationalFacts?: string;
  persona?: string;
}

export default function PreparationCollapsibleSection({
  situationalFacts,
  persona,
}: PreparationCollapsibleSectionProps) {
  const t = useTranslations('Preparation');

  return (
    <Accordion type="multiple" className="w-full space-y-3">
      {situationalFacts && (
        <AccordionItem
          value="situational-facts"
          className="border border-marigold-30 rounded-lg bg-white/50 shadow-sm"
        >
          <AccordionTrigger>{t('situationalFacts')}</AccordionTrigger>
          <AccordionContent className="px-5 pb-5">
            <div className="text-base leading-relaxed text-marigold-90">
              {situationalFacts.split('\n').map((line, index) => (
                <p key={index} className="mb-3 last:mb-0">
                  {line}
                </p>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      )}
      {persona && (
        <AccordionItem
          value="persona"
          className="border border-marigold-30 rounded-lg bg-white/50 shadow-sm"
        >
          <AccordionTrigger>{t('persona')}</AccordionTrigger>
          <AccordionContent className="px-5 pb-5">
            <div className="text-base leading-relaxed text-marigold-90">
              {persona.split('\n').map((line, index) => (
                <p key={index} className="mb-3 last:mb-0">
                  {line}
                </p>
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      )}
    </Accordion>
  );
}
