import { useTranslations } from 'next-intl';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { Badge } from '@/components/ui/Badge';
import Image from 'next/image';
import { DifficultyLevelEnums } from '@/interfaces/models/ConversationScenario';

interface PersonaCollapsibleSectionProps {
  situationalFacts?: string;
  persona?: string;
  categoryName?: string;
  difficultyLevel?: string;
  personaName?: string;
  difficultyLevelBadge?: DifficultyLevelEnums;
  imgSrc?: string;
}

export default function PersonaCollapsibleSection({
  situationalFacts,
  persona,
  categoryName,
  difficultyLevel,
  difficultyLevelBadge,
  personaName,
  imgSrc,
}: PersonaCollapsibleSectionProps) {
  const t = useTranslations('Preparation');

  return (
    <section className="flex flex-col gap-16 w-full border border-marigold-30 rounded-lg p-8 text-bw-70">
      <div className="flex items-center justify-between w-full">
        <div className="text-xl font-semibold">{categoryName}</div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 w-full px-2 text-bw-70 gap-y-16 sm:gap-y-1 gap-16">
        {(personaName || imgSrc) && (
          <div className="flex flex-col gap-y-0.5 items-center text-center sm:items-start sm:text-left">
            <div className="text-md font-bold mb-2 sm:pl-8 row-start-1">{t('otherPartyLabel')}</div>
            <div className="flex items-center gap-4 min-h-[56px] sm:pl-8 row-start-2">
              {imgSrc && (
                <Image
                  src={imgSrc}
                  width={52}
                  height={52}
                  alt={personaName || 'Persona'}
                  className="rounded-full bg-white border border-bw-20"
                />
              )}
              {personaName && <span className="text-xl font-medium">{personaName}</span>}
            </div>
          </div>
        )}
        {difficultyLevel && (
          <div className="flex flex-col gap-y-0.5 items-center text-center sm:items-start sm:text-left">
            <div className="text-md font-bold mb-2 sm:pl-8 row-start-3 sm:col-start-2 sm:row-start-1">
              {t('difficultyLabel')}
            </div>
            <div className="flex items-center min-h-[56px] sm:pl-8 row-start-4 sm:col-start-2 sm:row-start-2">
              <Badge variant={difficultyLevelBadge} className="whitespace-nowrap text-xl px-4 py-1">
                {difficultyLevel}
              </Badge>
            </div>
          </div>
        )}
      </div>

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
    </section>
  );
}
