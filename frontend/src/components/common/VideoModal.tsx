'use client';

import React from 'react';
import { Dialog, DialogContent } from '@/components/ui/Dialog';

interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoSrc: string;
}

export function VideoModal({ isOpen, onClose, videoSrc }: VideoModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl w-[95vw] h-[90vh] p-0 border-0 bg-black overflow-hidden">
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
