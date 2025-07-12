import React from 'react';

interface PersonalizationItem {
  title: string;
  description: string;
}

interface PersonalizationGroupProps {
  items: PersonalizationItem[];
  className?: string;
}

const PersonalizationGroup: React.FC<PersonalizationGroupProps> = ({ items, className }) => (
  <div className={`w-full flex flex-col lg:flex-row gap-10 px-2 ${className ?? ''}`}>
    {items.map((item, idx) => (
      <div className="flex-1" key={idx}>
        <div className="font-semibold text-bold mb-2">{item.title}</div>
        <div className="text-bw-70 text-base leading-relaxed">{item.description}</div>
      </div>
    ))}
  </div>
);

export default PersonalizationGroup;
