import { UserConfidenceField } from '@/interfaces/UserInputFields';
import Slider from '@/components/ui/Slider';
import { cn } from '@/lib/utils';

const UserConfidenceFields: React.FC<{ fields: UserConfidenceField[]; className?: string }> = ({
  fields,
  className,
}) => {
  return (
    <div className={cn('flex flex-col gap-10 w-full', className)}>
      {fields.map((field) => (
        <div key={field.title} className="flex flex-col gap-2">
          <span className="text-lg">{field.title}</span>
          <Slider
            className="w-full"
            min={field.minValue}
            max={field.maxValue}
            step={1}
            defaultValue={[50]}
            onValueChange={(value) => {
              if (field.onChange) {
                field.onChange(value);
              }
            }}
          />
          <div className="flex justify-between text-base text-bw-40">
            <span>{field.minLabel}</span>
            <span>{field.maxLabel}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default UserConfidenceFields;
