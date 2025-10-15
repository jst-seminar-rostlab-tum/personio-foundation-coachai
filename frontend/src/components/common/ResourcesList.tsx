import { Document } from '@/interfaces/models/Document';
import QuoteResourceItem from './QuoteResourceItem';

interface ResourcesListProps {
  resources: Document[];
  columns?: number;
}

export default function ResourcesList({ resources, columns = 1 }: ResourcesListProps) {
  return (
    <div className={`grid grid-cols-1 ${columns > 1 ? `md:grid-cols-${columns}` : ''} gap-2`}>
      {resources.map((resource, index) => {
        return <QuoteResourceItem key={resource.id || index} resource={resource} showCopyButton />;
      })}
    </div>
  );
}
