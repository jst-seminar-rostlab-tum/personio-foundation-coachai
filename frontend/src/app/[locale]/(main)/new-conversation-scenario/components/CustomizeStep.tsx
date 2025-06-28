import Image from 'next/image';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { useTranslations } from 'next-intl';
import { CustomizeStepProps } from '@/interfaces/CustomizeStepProps';

export function CustomizeStep({
  difficulty,
  emotionalTone,
  complexity,
  onDifficultyChange,
  onEmotionalToneChange,
  onComplexityChange,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario');
  const tCommon = useTranslations('Common');
  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('customize.title')}</div>
      <div className="text-lg text-font-dark text-center mb-2">
        {t('customize.difficulty.title')}
      </div>
      <RadioGroup
        value={difficulty}
        onValueChange={onDifficultyChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="d1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/difficulty-easy.svg" alt={t('easy')} width={56} height={56} />
          <span className="text-sm">{t('easy')}</span>
          <RadioGroupItem value="easy" id="d1" />
        </label>
        <label htmlFor="d2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/difficulty-medium.svg" alt={t('medium')} width={56} height={56} />
          <span className="text-sm">{t('medium')}</span>
          <RadioGroupItem value="medium" id="d2" />
        </label>
        <label htmlFor="d3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/difficulty-hard.svg" alt={t('hard')} width={56} height={56} />
          <span className="text-sm">{t('hard')}</span>
          <RadioGroupItem value="hard" id="d3" />
        </label>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">
        {t('customize.emotionalTone.title')}
      </div>
      <RadioGroup
        value={emotionalTone}
        onValueChange={onEmotionalToneChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="e1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/mood-positive.svg" alt={tCommon('positive')} width={56} height={56} />
          <span className="text-sm">{tCommon('positive')}</span>
          <RadioGroupItem value="positive" id="e1" />
        </label>
        <label htmlFor="e2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/mood-neutral.svg" alt={t('neutral')} width={56} height={56} />
          <span className="text-sm">{t('neutral')}</span>
          <RadioGroupItem value="neutral" id="e2" />
        </label>
        <label htmlFor="e3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/mood-negative.svg" alt={tCommon('negative')} width={56} height={56} />
          <span className="text-sm">{tCommon('negative')}</span>
          <RadioGroupItem value="negative" id="e3" />
        </label>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">
        {t('customize.complexity.title')}
      </div>
      <RadioGroup
        value={complexity}
        onValueChange={onComplexityChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="c1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/complexity-simple.svg" alt={t('simple')} width={56} height={56} />
          <span className="text-sm">{t('simple')}</span>
          <RadioGroupItem value="simple" id="c1" />
        </label>
        <label htmlFor="c2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/complexity-medium.svg" alt={t('medium')} width={56} height={56} />
          <span className="text-sm">{t('medium')}</span>
          <RadioGroupItem value="medium" id="c2" />
        </label>
        <label htmlFor="c3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image src="/icons/complexity-complex.svg" alt={t('complex')} width={56} height={56} />
          <span className="text-sm">{t('complex')}</span>
          <RadioGroupItem value="complex" id="c3" />
        </label>
      </RadioGroup>
    </div>
  );
}
