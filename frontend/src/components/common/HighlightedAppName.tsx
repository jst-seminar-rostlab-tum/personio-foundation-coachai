interface HighlightedAppNameProps {
  className?: string;
}

export function HighlightedAppName({ className = '' }: HighlightedAppNameProps) {
  return (
    <span className={className}>
      Coach<span className="text-forest-90">AI</span>
    </span>
  );
}
