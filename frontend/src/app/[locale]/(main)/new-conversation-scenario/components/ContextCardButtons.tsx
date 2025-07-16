import { ContextMode, ContextModeEnums } from '@/interfaces/models/ConversationScenario';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { useTranslations } from 'next-intl';

export default function ContextCardButtons() {
  const t = useTranslations('ConversationScenario');
  const { formState, updateForm } = useConversationScenarioStore();

  const contextModes = [
    {
      value: ContextModeEnums.DEFAULT,
      label: t('customize.context.default'),
      subtitle: t('customize.context.defaultSubtitle'),
    },
    {
      value: ContextModeEnums.CUSTOM,
      label: t('customize.context.custom'),
      subtitle: t('customize.context.customSubtitle'),
    },
  ];

  return (
    <div>
      <div className="text-xl text-font-dark text-center mb-8">{t('customizationTitle')}</div>
      <div className="max-w-4xl mx-auto">
        <div className="mb-10 w-full flex justify-center flex-col sm:flex-row gap-4 items-stretch">
          {contextModes.map((contextMode) => {
            const isSelected = formState.contextMode === contextMode.value;
            return (
              <button
                type="button"
                className={`box-border rounded-2xl flex flex-col items-start justify-start text-lg outline outline-2 outline-bw-20 cursor-pointer hover:bg-marigold-30/80 active:outline-none active:bg-marigold-30 disabled:pointer-events-none p-6 group ${isSelected ? 'outline-none bg-marigold-30' : ''} flex-1`}
                onClick={() => updateForm({ contextMode: contextMode.value as ContextMode })}
                key={contextMode.value}
              >
                <span className="text-xl text-bw-70 font-semibold mb-2 text-left">
                  {contextMode.label}
                </span>
                <span
                  className={`text-base leading-relaxed text-bw-40 group-hover:text-bw-70 ${isSelected ? 'text-bw-70' : ''} text-left`}
                >
                  {contextMode.subtitle}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
