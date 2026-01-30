'use client';

import { useEffect, useRef, useState } from 'react';
import { Document } from '@/interfaces/models/Document';
import QuoteResourceItem from './QuoteResourceItem';

/**
 * Props for the resources list component.
 */
interface ResourcesListProps {
  resources: Document[];
  columns?: number;
  enableScroll?: boolean;
}

/**
 * Renders a grid of resource cards with optional scrolling.
 */
export default function ResourcesList({
  resources,
  columns = 1,
  enableScroll = false,
}: ResourcesListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [maxHeight, setMaxHeight] = useState('400px');

  useEffect(() => {
    if (!enableScroll) {
      return () => {};
    }

    /**
     * Calculates a max height that fits two items.
     */
    const updateHeight = () => {
      if (!containerRef.current) return;

      const items = containerRef.current.querySelectorAll('[data-resource-item]');
      if (items.length === 0) return;

      const firstItem = items[0] as HTMLElement;
      let heightFor2Items = firstItem.offsetHeight;

      if (items.length >= 2) {
        const secondItem = items[1] as HTMLElement;
        const secondItemBottom = secondItem.offsetTop + secondItem.offsetHeight;
        heightFor2Items = secondItemBottom - firstItem.offsetTop;
      } else {
        heightFor2Items = firstItem.offsetHeight;
      }

      const buffer = 20;
      setMaxHeight(`${heightFor2Items + buffer}px`);
    };

    updateHeight();
    window.addEventListener('resize', updateHeight);

    return () => {
      window.removeEventListener('resize', updateHeight);
    };
  }, [resources, enableScroll]);

  return (
    <div
      ref={containerRef}
      className={`grid grid-cols-1 ${columns > 1 ? `md:grid-cols-${columns}` : ''} gap-2 ${enableScroll ? 'overflow-y-auto' : ''} items-stretch`}
      style={enableScroll ? { maxHeight } : undefined}
    >
      {resources.map((resource, index) => {
        return (
          <div key={resource.id || index} data-resource-item className="flex">
            <QuoteResourceItem resource={resource} showCopyButton />
          </div>
        );
      })}
    </div>
  );
}
