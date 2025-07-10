import { Download, Loader2 } from 'lucide-react';
import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { getDocsSignedUrl } from '@/services/ResourceService';
import { Button } from '../ui/Button';

interface ResourceItemProps {
  name: string;
}

const ResourceItem: React.FC<ResourceItemProps> = ({ name }) => {
  const t = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isLoading) return;
    setIsLoading(true);
    try {
      const response = await getDocsSignedUrl(api, name);
      const downloadUrl = response.url;
      const link = document.createElement('a');
      link.href = downloadUrl;
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
      </div>
      <Button
        variant="ghost"
        size="icon"
        onClick={handleDownload}
        disabled={isLoading}
        aria-label="Download resource"
      >
        {isLoading ? (
          <Loader2 className="w-6 h-6 animate-spin" />
        ) : (
          <Download className="w-6 h-6" />
        )}
      </Button>
    </div>
  );
};

export default ResourceItem;
