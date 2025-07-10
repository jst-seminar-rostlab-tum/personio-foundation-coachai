import ResourceItem from './ResourceItem';

interface ResourcesListProps {
  resources: string[];
}

export default function ResourcesList({ resources }: ResourcesListProps) {
  return (
    <div className="flex flex-col gap-4">
      {resources.map((name) => (
        <ResourceItem key={name} name={name} />
      ))}
    </div>
  );
}
