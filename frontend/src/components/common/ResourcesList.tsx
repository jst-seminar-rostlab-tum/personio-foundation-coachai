import { Resource } from '@/interfaces/models/Resource';
import ResourceItem from './ResourceItem';

interface ResourcesListProps {
  resources: Resource[];
}

export default function ResourcesList({ resources }: ResourcesListProps) {
  return (
    <div className="flex flex-col gap-4">
      {resources.map((resource) => (
        <ResourceItem
          key={resource.name}
          name={resource.name}
          author={resource.author}
          fileUrl={resource.fileUrl}
        />
      ))}
    </div>
  );
}
