import { UserPreference } from '@/interfaces/UserInputFields';
import { cn } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const UserPreferences: React.FC<{ preferences: UserPreference[]; className?: string }> = ({
  preferences,
  className,
}) => {
  return (
    <div className={cn('flex flex-col gap-12 w-full', className)}>
      {preferences.map((preference) => (
        <div key={preference.label} className="flex flex-col gap-2">
          <span className="text-lg">{preference.label}</span>
          <Select
            name={preference.label}
            defaultValue={preference.defaultValue}
            value={preference.value}
            onValueChange={(value) => {
              if (preference.onChange) {
                preference.onChange(value);
              }
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select an option" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                {preference.options.map((option) => (
                  <SelectItem key={option.code} value={option.code}>
                    {option.name}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      ))}
    </div>
  );
};

export default UserPreferences;
