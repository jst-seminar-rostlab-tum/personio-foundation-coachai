import { Download } from 'lucide-react';
import React from 'react';
import { useTranslations } from 'next-intl';
import { ResourceItemProps } from '@/interfaces/ResourceItemProps';

const ResourceItem: React.FC<ResourceItemProps> = ({ name, author, fileUrl }) => {
  const t = useTranslations('Common');
  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement('a');
    link.href = fileUrl;
    link.download = `${name}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="border border-bw-20 rounded-lg p-8 flex justify-between items-center gap-x-8 transition-all duration-300">
      <div className="flex flex-col gap-2">
        <h2 className="text-xl">{name}</h2>
        <p className="text-base text-bw-40">
          {t('resources.by')} <span className="font-semibold">{author}</span>
        </p>
      </div>
      <button
        onClick={handleDownload}
        className="flex items-center justify-center p-2 rounded hover:bg-bw-10 transition cursor-pointer"
        aria-label="Download resource"
        type="button"
      >
        <Download className="w-6 h-6" />
      </button>
    </div>
  );
};

export default ResourceItem;
