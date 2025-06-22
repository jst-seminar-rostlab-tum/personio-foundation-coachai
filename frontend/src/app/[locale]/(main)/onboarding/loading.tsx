import React from 'react';

export default function OnboardingPage() {
  return (
    <div className="flex flex-col max-w-2xl py-5 gap-5 mr-auto ml-auto">
      {/* Title and Subtitle */}
      <div className="flex flex-col gap-2 text-center">
        <div className="h-8 w-64 bg-bw-10 rounded-lg mx-auto animate-pulse" />
        <div className="h-5 w-96 bg-bw-10 rounded-lg mx-auto animate-pulse" />
      </div>

      {/* Stepper */}
      <div className="flex gap-2 mb-4 w-full max-w-md justify-center">
        {[1, 2, 3].map((_, i) => (
          <div key={i} className="flex flex-col items-center">
            <div className="w-7 h-7 bg-bw-20 rounded-full animate-pulse mb-1" />
            <div className="w-10 h-2 bg-bw-10 rounded animate-pulse" />
          </div>
        ))}
      </div>

      {/* Question */}
      <div className="h-6 w-2/3 bg-bw-10 rounded mx-auto animate-pulse" />

      {/* Options */}
      <div className="w-full max-w-md space-y-2 mx-auto">
        {[1, 2, 3, 4].map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="w-4 h-4 bg-bw-20 rounded-full animate-pulse" />
            <div className="flex-1 h-4 bg-bw-10 rounded animate-pulse" />
          </div>
        ))}
      </div>

      {/* Navigation Buttons */}
      <div className="flex w-full max-w-md gap-2 mx-auto">
        <div className="flex-1 h-9 bg-bw-10 rounded animate-pulse" />
        <div className="flex-1 h-9 bg-bw-20 rounded animate-pulse" />
      </div>

      {/* Skip Link */}
      <div className="flex justify-center">
        <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
      </div>
    </div>
  );
}
