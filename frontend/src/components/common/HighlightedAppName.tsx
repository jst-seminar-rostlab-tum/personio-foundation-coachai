interface HighlightedAppNameProps {
  className?: string;
}

export function HighlightedAppName({ className = '' }: HighlightedAppNameProps) {
  return (
    <span className={className}>
      Coach<span className="text-marigold-50">AI</span>
    </span>
  );
}
