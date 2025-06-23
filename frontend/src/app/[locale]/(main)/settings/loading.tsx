import React from 'react';

export default function SettingsLoadingPage() {
  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="h-7 w-24 bg-bw-10 rounded animate-pulse" />
        <div className="h-9 w-32 bg-bw-10 rounded animate-pulse" />
      </div>

      {/* Title */}
      <div className="h-8 w-32 bg-bw-10 rounded mb-6 animate-pulse" />

      {/* Accordion Sections */}
      <div className="mt-6 space-y-4">
        {/* Privacy Controls Accordion */}
        <div className="border border-bw-20 rounded-lg">
          <div className="flex items-center justify-between p-4 cursor-pointer">
            <div className="h-5 w-32 bg-bw-10 rounded animate-pulse" />
            <div className="h-5 w-5 bg-bw-10 rounded-full animate-pulse" />
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between w-full px-2">
                <div className="flex flex-col">
                  <div className="h-4 w-32 bg-bw-10 rounded mb-1 animate-pulse" />
                  <div className="h-3 w-24 bg-bw-10 rounded animate-pulse" />
                </div>
                <div className="h-6 w-12 bg-bw-20 rounded animate-pulse" />
              </div>
              <div className="flex items-center justify-between w-full px-2">
                <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
                <div className="h-8 w-20 bg-bw-10 rounded animate-pulse" />
              </div>
              <div className="flex items-center justify-between w-full px-2">
                <div className="h-4 w-28 bg-bw-10 rounded animate-pulse" />
                <div className="h-8 w-32 bg-bw-10 rounded animate-pulse" />
              </div>
            </div>
          </div>
        </div>

        {/* Personalization Settings Accordion */}
        <div className="border border-bw-20 rounded-lg">
          <div className="flex items-center justify-between p-4 cursor-pointer">
            <div className="h-5 w-48 bg-bw-10 rounded animate-pulse" />
            <div className="h-5 w-5 bg-bw-10 rounded-full animate-pulse" />
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div className="h-4 w-32 bg-bw-10 rounded mb-2 animate-pulse" />
              <div className="space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-4 h-4 bg-bw-20 rounded-full animate-pulse" />
                    <div className="flex-1 h-4 bg-bw-10 rounded animate-pulse" />
                  </div>
                ))}
              </div>
              <div className="h-px bg-bw-20 my-4" />
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex flex-col gap-2">
                    <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
                    <div className="h-8 w-full bg-bw-10 rounded animate-pulse" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 w-full">
        <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
      </div>
    </div>
  );
}
