import { Download, Loader2 } from 'lucide-react';
import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Resource } from '@/interfaces/models/Resource';
import { showErrorToast } from '@/lib/utils/toast';

const ResourceItem: React.FC<Resource> = ({ name, author, fileUrl }) => {
  const t = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (isLoading) return;

    setIsLoading(true);

    try {
      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = `${name}.pdf`;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      showErrorToast(error, t('resources.downloadError'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="border border-bw-20 rounded-lg p-8 flex justify-between items-center gap-x-8 transition-all duration-300">
      <div className="flex flex-col gap-2">
        <h2 className="text-xl">{name}</h2>
        {author && (
          <p className="text-base text-bw-40">
            {t('resources.by')} <span className="font-semibold">{author}</span>
          </p>
        )}
      </div>
      <button
        onClick={handleDownload}
        disabled={isLoading}
        className="flex items-center justify-center p-2 rounded hover:bg-bw-10 transition cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Download resource"
        type="button"
      >
        {isLoading ? (
          <Loader2 className="w-6 h-6 animate-spin" />
        ) : (
          <Download className="w-6 h-6" />
        )}
      </button>
    </div>
  );
};

export default ResourceItem;
