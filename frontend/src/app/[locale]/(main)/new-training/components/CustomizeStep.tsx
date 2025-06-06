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
  const t = useTranslations('NewTraining.customize');

  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('title')}</div>
      <div className="text-lg text-font-dark text-center mb-2">{t('difficulty.title')}</div>
      <RadioGroup
        value={difficulty}
        onValueChange={onDifficultyChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/custom-category.svg"
            alt={t('difficulty.options.easy')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.easy')}</span>
          <RadioGroupItem value="easy" id="d1" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/custom-category.svg"
            alt={t('difficulty.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.medium')}</span>
          <RadioGroupItem value="medium" id="d2" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/custom-category.svg"
            alt={t('difficulty.options.hard')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.hard')}</span>
          <RadioGroupItem value="hard" id="d3" />
        </div>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">{t('emotionalTone.title')}</div>
      <RadioGroup
        value={emotionalTone}
        onValueChange={onEmotionalToneChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/positive.svg"
            alt={t('emotionalTone.options.positive')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.positive')}</span>
          <RadioGroupItem value="positive" id="e1" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/neutral.svg"
            alt={t('emotionalTone.options.neutral')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.neutral')}</span>
          <RadioGroupItem value="neutral" id="e2" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/negative.svg"
            alt={t('emotionalTone.options.negative')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.negative')}</span>
          <RadioGroupItem value="negative" id="e3" />
        </div>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">{t('complexity.title')}</div>
      <RadioGroup
        value={complexity}
        onValueChange={onComplexityChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/simple.svg"
            alt={t('complexity.options.simple')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.simple')}</span>
          <RadioGroupItem value="simple" id="c1" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/medium.svg"
            alt={t('complexity.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.medium')}</span>
          <RadioGroupItem value="medium" id="c2" />
        </div>
        <div className="flex flex-col items-center space-y-2">
          <Image
            src="/icons/complex.svg"
            alt={t('complexity.options.complex')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.complex')}</span>
          <RadioGroupItem value="complex" id="c3" />
        </div>
      </RadioGroup>
    </div>
  );
}
