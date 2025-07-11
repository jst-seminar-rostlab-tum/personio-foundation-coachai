import ResourceItem from './ResourceItem';

interface ResourcesListProps {
  resources: string[];
  columns?: number;
}

export default function ResourcesList({ resources, columns = 1 }: ResourcesListProps) {
  return (
    <div className={`grid grid-cols-1 ${columns > 1 ? `md:grid-cols-${columns}` : ''} gap-2`}>
      {resources.map((name) => (
        <ResourceItem key={name} name={name} />
      ))}
    </div>
  );
}
