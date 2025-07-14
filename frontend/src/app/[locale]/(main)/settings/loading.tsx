import React from 'react';

export default function SettingsLoadingPage() {
  return (
    <div className="mx-auto pt-8">
      {/* Title */}
      <div className="h-10 w-56 bg-bw-10 rounded-lg mb-10 animate-pulse" />

      {/* Privacy Controls Section */}
      <div className="mb-12">
        <div className="h-6 w-40 bg-bw-10 rounded mb-6 animate-pulse" /> {/* Section Title */}
        <div className="flex flex-col gap-10 pl-2">
          {/* Store Conversation Audio and Transcripts */}
          <div className="flex items-center justify-between w-full">
            <div>
              <div className="h-5 w-64 bg-bw-10 rounded mb-2 animate-pulse" />
              <div className="h-4 w-96 bg-bw-10 rounded animate-pulse" />
            </div>
            <div className="h-6 w-12 bg-bw-10 rounded-full animate-pulse" />
          </div>
          {/* Export Personal Data */}
          <div className="flex items-center justify-between w-full">
            <div className="h-5 w-48 bg-bw-10 rounded animate-pulse" />
            <div className="h-10 w-24 bg-bw-10 rounded animate-pulse" />
          </div>
          {/* Delete Account */}
          <div className="flex items-center justify-between w-full">
            <div className="h-5 w-40 bg-bw-10 rounded animate-pulse" />
            <div className="h-10 w-40 bg-bw-10 rounded animate-pulse" />
          </div>
        </div>
      </div>

      {/* Personalization Settings Section */}
      <div className="mb-12">
        <div className="h-6 w-64 bg-bw-10 rounded mb-6 animate-pulse" /> {/* Section Title */}
        <div className="flex flex-col gap-8 pl-2">
          {/* Current Role */}
          <div className="flex flex-col gap-2">
            <div className="h-5 w-32 bg-bw-10 rounded mb-2 animate-pulse" />
            <div className="h-10 w-80 bg-bw-10 rounded animate-pulse" />
          </div>
          {/* Primary Goals */}
          <div className="flex flex-col gap-2">
            <div className="h-5 w-32 bg-bw-10 rounded mb-2 animate-pulse" />
            <div className="h-10 w-80 bg-bw-10 rounded animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}
