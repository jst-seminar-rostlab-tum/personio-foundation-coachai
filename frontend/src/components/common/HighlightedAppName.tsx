/**
 * Props for the highlighted app name mark.
 */
interface HighlightedAppNameProps {
  className?: string;
}

/**
 * Renders the CoachAI brand name with accent styling.
 */
export function HighlightedAppName({ className = '' }: HighlightedAppNameProps) {
  return (
    <span className={className}>
      Coach<span className="text-forest-90">AI</span>
    </span>
  );
}
