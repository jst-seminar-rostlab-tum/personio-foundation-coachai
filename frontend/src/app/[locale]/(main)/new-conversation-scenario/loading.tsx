import React from 'react';

export default function ConversationScenarioPageLoading() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Title */}
      <div className="text-2xl text-font-dark text-center w-full mb-8">
        <div className="h-8 w-64 bg-bw-10 rounded-lg mx-auto animate-pulse" />
      </div>

      {/* Stepper */}
      <div className="flex justify-between items-center mb-16 w-full mx-auto max-w-md">
        <div className="flex items-center w-full">
          <div className="w-10 h-10 rounded-full bg-bw-20 flex-shrink-0 animate-pulse" />
          <div className="flex-1 h-1 bg-bw-10 mx-2" />
          <div className="w-10 h-10 rounded-full bg-bw-10 flex-shrink-0 animate-pulse" />
          <div className="flex-1 h-1 bg-bw-10 mx-2" />
          <div className="w-10 h-10 rounded-full bg-bw-10 flex-shrink-0 animate-pulse" />
        </div>
      </div>

      {/* Category Step - 2x2 Grid */}
      <div className="grid grid-cols-2 gap-4 w-full mx-auto mb-8 md:max-w-lg xl:max-w-xl">
        {[1, 2, 3, 4].map((_, i) => (
          <div
            key={i}
            className="aspect-square bg-bw-10 rounded-lg flex items-center justify-center animate-pulse"
          >
            <div className="w-2/3 h-2/3 bg-bw-20 rounded" />
          </div>
        ))}
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-4 w-full md:max-w-lg xl:max-w-xl mx-auto">
        <div className="flex-1 h-10 bg-bw-10 rounded animate-pulse" />
        <div className="flex-1 h-10 bg-bw-20 rounded animate-pulse" />
      </div>
    </div>
  );
}
