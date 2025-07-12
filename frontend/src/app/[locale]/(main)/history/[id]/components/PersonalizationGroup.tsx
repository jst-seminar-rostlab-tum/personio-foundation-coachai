import React from 'react';
import Image from 'next/image';

interface PersonalizationItem {
  title: string;
  description: string;
}

interface PersonalizationGroupProps {
  items: PersonalizationItem[];
  className?: string;
  personaImage?: string;
  personaName?: string;
}

const PersonalizationGroup: React.FC<PersonalizationGroupProps> = ({
  items,
  className,
  personaImage,
  personaName,
}) => (
  <div className={`w-full flex flex-col ${className ?? ''}`}>
    {personaImage && personaName && (
      <div className="flex items-center gap-4 mb-10">
        <Image
          src={personaImage}
          alt={personaName}
          width={64}
          height={64}
          className="rounded-full bg-white"
        />
        <span className="font-bold text-2xl">{personaName}</span>
      </div>
    )}
    <div className="flex flex-col lg:flex-row gap-10 px-2 w-full">
      {items.map((item, idx) => (
        <div className="flex-1" key={idx}>
          <div className="font-semibold text-bold mb-2">{item.title}</div>
          <div className="text-bw-70 text-base leading-relaxed">{item.description}</div>
        </div>
      ))}
    </div>
  </div>
);

export default PersonalizationGroup;
