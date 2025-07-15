import { useTranslations } from 'next-intl';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { Badge } from '@/components/ui/Badge';
import { Avatar, AvatarImage } from '@/components/ui/Avatar';
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
    <section className="flex flex-col gap-6 bg-marigold-5 border border-marigold-30 rounded-lg p-6 text-marigold-95">
      <div className="flex items-center gap-2 justify-between">
        <h2 className="text-xl font-semibold">{categoryName}</h2>

        {difficultyLevel && (
          <Badge variant={difficultyLevelBadge} className="whitespace-nowrap mt-1 sm:mt-0">
            {difficultyLevel}
          </Badge>
        )}
      </div>

      {(personaName || imgSrc) && (
        <div className="flex flex-col items-center">
          {imgSrc && (
            <Avatar>
              <AvatarImage src={imgSrc} />
            </Avatar>
          )}
          {personaName && <span className="font-bold text-md text-bw-90 mt-1">{personaName}</span>}
        </div>
      )}

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
