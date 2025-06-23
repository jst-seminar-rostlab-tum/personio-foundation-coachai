import { KeyConcept } from '@/interfaces/ConversationScenario';

export default function PreparationKeyConcepts({ keyConcepts }: { keyConcepts: KeyConcept[] }) {
  return (
    <div className="space-y-8">
      {keyConcepts.map((concept, index) => (
        <div key={index} className="flex flex-col gap-2">
          <label
            htmlFor={`check-${index}`}
            className="text-lg font-bold text-bw-70 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            {concept.header}
          </label>
          <p className="text-base text-bw-70">{concept.value}</p>
        </div>
      ))}
    </div>
  );
}
