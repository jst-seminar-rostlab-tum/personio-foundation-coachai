import { UserPreference } from '@/interfaces/models/UserInputFields';
import { cn } from '@/lib/utils/cnMerge';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';
import { MultiSelect } from '@/components/ui/MultiSelect';

/**
 * Props for the user preferences selection controls.
 */
interface UserPreferencesProps {
  currentRole: UserPreference;
  primaryGoals: UserPreference<string[]>;
  className?: string;
}

/**
 * Renders role and primary goal selectors.
 */
const UserPreferences: React.FC<UserPreferencesProps> = ({
  currentRole,
  primaryGoals,
  className,
}) => {
  return (
    <div className={cn('flex flex-col gap-12 w-full', className)}>
      <div key={currentRole.label} className="flex flex-col gap-2">
        <span className="text-lg">{currentRole.label}</span>
        <Select
          name={currentRole.label}
          defaultValue={currentRole.defaultValue}
          value={currentRole.value}
          onValueChange={(value) => {
            if (currentRole.onChange) {
              currentRole.onChange(value);
            }
          }}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select an option" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {currentRole.options.map((option) => (
                <SelectItem key={option.id} value={option.id}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      <div key={primaryGoals.label} className="flex flex-col gap-2">
        <span className="text-lg">{primaryGoals.label}</span>
        <MultiSelect
          options={primaryGoals.options}
          value={primaryGoals.value!}
          maxSelected={3}
          placeholder={primaryGoals.placeholder}
          maxSelectedDisclaimer={primaryGoals.maxSelectedDisclaimer}
          onChange={(value) => {
            if (primaryGoals.onChange) {
              primaryGoals.onChange(value);
            }
          }}
        />
      </div>
    </div>
  );
};

export default UserPreferences;
