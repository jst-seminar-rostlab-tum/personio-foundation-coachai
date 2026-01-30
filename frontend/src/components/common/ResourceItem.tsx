import { Download, Loader2, FileText } from 'lucide-react';
import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { getDocsSignedUrl } from '@/services/ResourceService';
import { Button } from '../ui/Button';

/**
 * Props for a resource list item.
 */
interface ResourceItemProps {
  name: string;
}

/**
 * Renders a resource row with download action.
 */
const ResourceItem: React.FC<ResourceItemProps> = ({ name }) => {
  const t = useTranslations('Common');
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Requests a signed URL and triggers a file download.
   */
  const handleDownload = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (isLoading) return;
    setIsLoading(true);
    const fileName = `${name}.pdf`;
    try {
      const response = await getDocsSignedUrl(api, fileName);
      const downloadUrl = response.url;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName;
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
    <div
      onClick={handleDownload}
      className="w-full flex items-center justify-between py-2 px-4 rounded-lg border border-bw-40 hover:border-bw-30 hover:bg-custom-beige/50 transition-all duration-200 ease-in-out cursor-pointer group"
    >
      <div className="flex items-center gap-3 flex-1">
        <FileText className="w-4 h-4 text-bw-50 group-hover:text-bw-70 transition-colors duration-200" />
        <span className="text-sm font-medium group-hover:underline transition-all duration-200">
          {name}
        </span>
      </div>

      <Button
        variant="ghost"
        size="icon"
        disabled={isLoading}
        className="bg-forest-90 hover:bg-forest-90"
        aria-label={`Download ${name}`}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin text-white" />
        ) : (
          <Download className="w-5 h-5 text-white" />
        )}
      </Button>
    </div>
  );
};

export default ResourceItem;
