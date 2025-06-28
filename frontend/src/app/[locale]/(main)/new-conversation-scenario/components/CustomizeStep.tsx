import Image from 'next/image';
import { RadioGroup, RadioGroupItem } from '@/components/ui/RadioGroup';
import { useTranslations } from 'next-intl';

interface CustomizeStepProps {
  difficulty: string;
  emotionalTone: string;
  complexity: string;
  onDifficultyChange: (difficulty: string) => void;
  onEmotionalToneChange: (emotionalTone: string) => void;
  onComplexityChange: (complexity: string) => void;
}

export function CustomizeStep({
  difficulty,
  emotionalTone,
  complexity,
  onDifficultyChange,
  onEmotionalToneChange,
  onComplexityChange,
}: CustomizeStepProps) {
  const t = useTranslations('ConversationScenario.customize');

  return (
    <div>
      <div className="text-xl text-font-dark text-center w-full mb-8">{t('title')}</div>
      <div className="text-lg text-font-dark text-center mb-2">{t('difficulty.title')}</div>
      <RadioGroup
        value={difficulty}
        onValueChange={onDifficultyChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="d1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/difficulty/easy.svg"
            alt={t('difficulty.options.easy')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.easy')}</span>
          <RadioGroupItem value="easy" id="d1" />
        </label>
        <label htmlFor="d2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/difficulty/medium.svg"
            alt={t('difficulty.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.medium')}</span>
          <RadioGroupItem value="medium" id="d2" />
        </label>
        <label htmlFor="d3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/difficulty/hard.svg"
            alt={t('difficulty.options.hard')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('difficulty.options.hard')}</span>
          <RadioGroupItem value="hard" id="d3" />
        </label>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">{t('emotionalTone.title')}</div>
      <RadioGroup
        value={emotionalTone}
        onValueChange={onEmotionalToneChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="e1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/mood/positive.svg"
            alt={t('emotionalTone.options.positive')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.positive')}</span>
          <RadioGroupItem value="positive" id="e1" />
        </label>
        <label htmlFor="e2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/mood/neutral.svg"
            alt={t('emotionalTone.options.neutral')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.neutral')}</span>
          <RadioGroupItem value="neutral" id="e2" />
        </label>
        <label htmlFor="e3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/mood/negative.svg"
            alt={t('emotionalTone.options.negative')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('emotionalTone.options.negative')}</span>
          <RadioGroupItem value="negative" id="e3" />
        </label>
      </RadioGroup>

      <div className="text-lg text-font-dark text-center mb-2">{t('complexity.title')}</div>
      <RadioGroup
        value={complexity}
        onValueChange={onComplexityChange}
        className="mb-8 flex flex-row justify-between gap-4"
      >
        <label htmlFor="c1" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/complexity/simple.svg"
            alt={t('complexity.options.simple')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.simple')}</span>
          <RadioGroupItem value="simple" id="c1" />
        </label>
        <label htmlFor="c2" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/complexity/medium.svg"
            alt={t('complexity.options.medium')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.medium')}</span>
          <RadioGroupItem value="medium" id="c2" />
        </label>
        <label htmlFor="c3" className="flex flex-col items-center space-y-2 cursor-pointer">
          <Image
            src="/images/complexity/complex.svg"
            alt={t('complexity.options.complex')}
            width={56}
            height={56}
          />
          <span className="text-sm">{t('complexity.options.complex')}</span>
          <RadioGroupItem value="complex" id="c3" />
        </label>
      </RadioGroup>
    </div>
  );
}
