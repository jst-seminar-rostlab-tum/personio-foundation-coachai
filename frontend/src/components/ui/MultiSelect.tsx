'use client';

import * as React from 'react';
import { X } from 'lucide-react';

import { Badge } from '@/components/ui/Badge';
import { Command, CommandGroup, CommandItem, CommandList } from '@/components/ui/Command';
import { Command as CommandPrimitive } from 'cmdk';
import { UserOption } from '@/interfaces/models/UserInputFields';

interface MultiSelectProps {
  options: UserOption[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  maxSelectedDisclaimer?: string;
  maxSelected?: number;
}

export function MultiSelect({
  options,
  value,
  onChange,
  placeholder,
  maxSelected,
  maxSelectedDisclaimer,
}: MultiSelectProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const wrapperRef = React.useRef<HTMLDivElement>(null);
  const [open, setOpen] = React.useState(false);
  const [inputValue, setInputValue] = React.useState('');

  const selectables = options.filter((option) => !value.includes(option.id));

  React.useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) return () => {};

    const handleFocusIn = () => setOpen(true);
    const handleFocusOut = (e: FocusEvent) => {
      if (!wrapper.contains(e.relatedTarget as Node)) {
        setOpen(false);
      }
    };

    wrapper.addEventListener('focusin', handleFocusIn);
    wrapper.addEventListener('focusout', handleFocusOut);

    return () => {
      wrapper.removeEventListener('focusin', handleFocusIn);
      wrapper.removeEventListener('focusout', handleFocusOut);
    };
  }, []);

  const handleUnselect = (optionId: string) => {
    onChange(value.filter((s) => s !== optionId));
    // Removed inputRef.current?.focus() to prevent dropdown from opening on badge removal
  };

  const handleKeyDown = React.useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      const input = inputRef.current;
      if (input) {
        if (e.key === 'Delete' || e.key === 'Backspace') {
          if (input.value === '') {
            onChange(value.slice(0, -1));
          }
        }
        if (e.key === 'Escape') {
          input.blur();
        }
      }
    },
    [value, onChange]
  );

  const handleWrapperClick = () => {
    if (selectables.length > 0 && value.length < (maxSelected ?? Infinity)) {
      inputRef.current?.focus();
    }
    setOpen(true);
  };

  const handleBlur = (e: React.FocusEvent) => {
    if (!wrapperRef.current?.contains(e.relatedTarget as Node)) {
      setOpen(false);
    }
  };

  return (
    <Command onKeyDown={handleKeyDown} className="overflow-visible bg-transparent">
      <div
        ref={wrapperRef}
        tabIndex={-1}
        className="group rounded-md border border-bw-40 bg-custom-beige px-3 py-2 text-sm ring-offset-custom-beige focus-within:ring-2 focus-within:ring-bw-40 focus-within:ring-offset-2 flex items-center flex-wrap gap-1 cursor-pointer"
        onClick={handleWrapperClick}
        onBlur={handleBlur}
      >
        {value.length < (maxSelected ?? Infinity) ? (
          <CommandPrimitive.Input
            ref={inputRef}
            value={inputValue}
            onValueChange={setInputValue}
            placeholder={placeholder ?? 'Select options...'}
            className="flex-1 bg-custom-beige outline-none placeholder:text-muted-foreground"
          />
        ) : (
          <span className="text-sm text-bw-70">{maxSelectedDisclaimer}</span>
        )}
      </div>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {value.map((optionId) => (
            <Badge key={optionId}>
              {options.find((option) => option.id === optionId)?.label || ''}
              <div
                className="ml-1 cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleUnselect(optionId);
                }}
              >
                <X className="h-3 w-3 text-muted-foreground hover:text-flame-50" />
              </div>
            </Badge>
          ))}
        </div>
      )}

      <div className="relative mt-2">
        <CommandList>
          {open && selectables.length > 0 && (
            <div className="absolute top-0 z-10 w-full rounded-md border bg-custom-beige text-popover-foreground shadow-md outline-none">
              <CommandGroup className="h-full overflow-auto">
                {selectables.map((option) => (
                  <CommandItem
                    key={option.id}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onSelect={() => {
                      inputRef.current?.focus();
                      onChange(
                        value.length < (maxSelected ?? Infinity) ? [...value, option.id] : value
                      );
                    }}
                    className="cursor-pointer hover:bg-bw-40"
                  >
                    {option.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </div>
          )}
        </CommandList>
      </div>
    </Command>
  );
}
