'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { Dialog, DialogContent, DialogTitle, DialogHeader } from '@/components/ui/Dialog';

/**
 * Props for the video modal.
 */
interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoSrc: string;
}

/**
 * Displays a full-screen modal with an embedded video player.
 */
export function VideoModal({ isOpen, onClose, videoSrc }: VideoModalProps) {
  const t = useTranslations('Common.videoModal');

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="max-w-6xl w-[95vw] h-[90vh] p-0 border-0 bg-black overflow-hidden"
        closeButtonClassName="text-white opacity-100 hover:bg-white/20"
      >
        <DialogHeader className="absolute top-4 left-4 z-10 pointer-events-none max-w-[calc(100%-4rem)]">
          <DialogTitle className="text-white text-xl font-semibold">{t('title')}</DialogTitle>
          <p className="text-white/70 text-sm mt-1">{t('description')}</p>
        </DialogHeader>

        <div className="relative w-full h-full">
          <video
            className="w-full h-full object-contain"
            controls
            preload="metadata"
            onEnded={onClose}
            poster=""
          >
            <source src={videoSrc} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      </DialogContent>
    </Dialog>
  );
}
