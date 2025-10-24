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
    <section className="flex flex-col gap-12 w-full border border-marigold-30 rounded-lg p-8 text-bw-70">
      <div className="flex items-center justify-between w-full">
        <div className="text-xl font-bold text-center w-full">{categoryName}</div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 w-full text-bw-70 gap-y-16 sm:gap-y-1">
        {(personaName || imgSrc) && (
          <div className="flex flex-col gap-y-0.5 items-center text-center sm:items-start sm:text-left">
            <div className="text-md font-semibold mb-2 sm:pl-16 row-start-1">
              {t('otherPartyLabel')}
            </div>
            <div className="flex items-center gap-4 min-h-[56px] sm:pl-16 row-start-2">
              {imgSrc && (
                <Image
                  src={imgSrc}
                  width={52}
                  height={52}
                  alt={personaName || 'Persona'}
                  className="rounded-full bg-white border border-bw-40"
                />
              )}
              {personaName && <span className="text-xl font-normal">{personaName}</span>}
            </div>
          </div>
        )}
        {difficultyLevel && (
          <div className="flex flex-col gap-y-0.5 items-center text-center sm:items-start sm:text-left">
            <div className="text-md font-semibold mb-2 sm:pl-16 row-start-3 sm:col-start-2 sm:row-start-1">
              {t('difficultyLabel')}
            </div>
            <div className="flex items-center min-h-[56px] sm:pl-16 row-start-4 sm:col-start-2 sm:row-start-2">
              <Badge variant={difficultyLevelBadge} className="whitespace-nowrap text-xl px-4 py-1">
                {difficultyLevel}
              </Badge>
            </div>
          </div>
        )}
      </div>

      <Accordion type="multiple" className="w-full space-y-4">
        {situationalFacts && (
          <AccordionItem value="situational-facts">
            <AccordionTrigger>
              <span className="text-md font-semibold">{t('situationalFacts')}</span>
            </AccordionTrigger>
            <AccordionContent className="px-4">
              <div className="text-base leading-relaxed">
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
          <AccordionItem value="persona">
            <AccordionTrigger>
              <span className="text-md font-semibold">{t('persona')}</span>
            </AccordionTrigger>
            <AccordionContent className="px-4">
              <div className="text-base leading-relaxed">
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
