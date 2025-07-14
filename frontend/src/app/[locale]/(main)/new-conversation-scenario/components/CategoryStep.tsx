'use client';

import { useTranslations } from 'next-intl';
import { Textarea } from '@/components/ui/Textarea';
import { useConversationScenarioStore } from '@/store/ConversationScenarioStore';
import { Categories } from '@/lib/constants/categories';
import { ContextModeEnums } from '@/interfaces/models/ConversationScenario';
import { PersonaButton } from './PersonaButton';

export function CategoryStep() {
  const t = useTranslations('ConversationScenario');
  const categories = Categories();
  const { formState, updateForm } = useConversationScenarioStore();
  const isCustomContextMode = formState.contextMode === ContextModeEnums.CUSTOM;

  const contextClass = `border border-bw-40 placeholder:text-muted-foreground flex field-sizing-content w-full rounded-md bg-white px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none ${isCustomContextMode ? '' : 'text-bw-60 cursor-not-allowed'} resize-none overflow-auto`;

  return (
    <div className="space-y-8">
      <div className="text-xl text-font-dark text-center">{t('situationTitle')}</div>
      <div className="grid grid-cols-2  lg:grid-cols-4 gap-5 w-full mx-auto">
        {Object.values(categories).map((category) => (
          <PersonaButton
            key={category.id}
            onClick={() =>
              updateForm({
                category: category.id,
                name: category.name,
                situationalFacts: category.defaultContext,
              })
            }
            selected={formState.category === category.id}
            image={category.iconUri}
            label={category.name}
          />
        ))}
      </div>
      {formState.category && (
        <div className="mt-8 mb-8">
          <div className="mb-4 font-medium text-xl">{t('selectContext')}</div>
          <Textarea
            className={contextClass}
            value={formState.situationalFacts}
            onChange={
              isCustomContextMode
                ? (e) => {
                    updateForm({ situationalFacts: e.target.value });
                  }
                : undefined
            }
            rows={16}
            readOnly={!isCustomContextMode}
            disabled={!isCustomContextMode}
          />
        </div>
      )}
    </div>
  );
}
