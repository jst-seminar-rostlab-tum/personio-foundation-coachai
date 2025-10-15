import { Quote, ExternalLink, BookOpen, Copy, Check } from 'lucide-react';
import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Document } from '@/interfaces/models/Document';
import { showErrorToast } from '@/lib/utils/toast';
import { api } from '@/services/ApiClient';
import { getDocsSignedUrl } from '@/services/ResourceService';
import { Button } from '../ui/Button';

interface QuoteResourceItemProps {
  resource: Document;
  showCopyButton?: boolean;
}

const QuoteResourceItem: React.FC<QuoteResourceItemProps> = ({
  resource,
  showCopyButton = true,
}) => {
  const t = useTranslations('Common');
  const [copied, setCopied] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleCopyQuote = async () => {
    try {
      await navigator.clipboard.writeText(resource.quote);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error(t('resources.copyError'), error);
    }
  };

  const handleDownload = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (isDownloading || !resource.title) return;

    setIsDownloading(true);
    const fileName = `${resource.title}.pdf`;
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
      setIsDownloading(false);
    }
  };

  return (
    <div className="w-full p-4 rounded-lg border border-bw-20 hover:border-bw-30 hover:bg-bw-10/50 transition-all duration-200 ease-in-out group">
      <div className="flex items-start gap-3 mb-3">
        <Quote className="w-5 h-5 text-marigold-60 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-bw-80 mb-1">{resource.title}</h4>
          {resource.author && (
            <p className="text-xs text-bw-50 mb-2">
              {t('resources.by')} {resource.author}
            </p>
          )}
        </div>
        {showCopyButton && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleCopyQuote}
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            aria-label={t('resources.copyQuote')}
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-600" />
            ) : (
              <Copy className="w-4 h-4 text-bw-50" />
            )}
          </Button>
        )}
      </div>

      <blockquote className="text-sm text-bw-70 italic border-l-2 border-marigold-30 pl-3 mb-3">
        &ldquo;{resource.quote}&rdquo;
      </blockquote>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 text-xs text-bw-50">
          {resource.page && (
            <div className="flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              <span>
                {t('resources.page')} {resource.page}
              </span>
            </div>
          )}
          {resource.chapter && (
            <div className="flex items-center gap-1">
              <span>{resource.chapter}</span>
            </div>
          )}
        </div>

        {resource.title && (
          <Button
            variant="ghost"
            size="icon"
            onClick={handleDownload}
            className="text-xs text-bw-50 hover:text-bw-70"
          >
            <ExternalLink className="w-3 h-3 mr-1" />
            {t('resources.viewSource')}
          </Button>
        )}
      </div>
    </div>
  );
};

export default QuoteResourceItem;
