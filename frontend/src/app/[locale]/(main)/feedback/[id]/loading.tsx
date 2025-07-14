import React from 'react';

export default function FeedbackDetailLoadingPage() {
  return (
    <div className="flex flex-col items-center w-full gap-8 px-4 pb-8">
      {/* Title */}
      <div className="h-8 w-48 bg-bw-10 rounded-lg mt-8 mb-2 self-start animate-pulse" />

      {/* Banner */}
      <div className="w-full bg-bw-10 rounded-lg flex flex-col items-center py-8 mb-4">
        <div className="h-7 w-80 bg-bw-20 rounded-lg mb-3 animate-pulse" />
        <div className="h-5 w-40 bg-bw-20 rounded-lg animate-pulse" />
      </div>

      {/* Score and Bars */}
      <div className="flex flex-col md:flex-row w-full gap-8 items-center mb-4">
        {/* Solid Circle Score */}
        <div className="flex justify-center items-center w-full md:w-1/3">
          <div className="w-48 h-48 rounded-full bg-bw-10 flex items-center justify-center animate-pulse">
            <div className="h-12 w-24 bg-bw-20 rounded-lg animate-pulse" />
          </div>
        </div>
        {/* Bars */}
        <div className="flex-1 flex flex-col gap-6 w-full">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex flex-col gap-2">
              <div className="h-5 w-32 bg-bw-10 rounded-lg animate-pulse mb-1" />
              <div className="h-4 w-full max-w-lg bg-bw-10 rounded-lg animate-pulse" />
            </div>
          ))}
        </div>
      </div>

      {/* Replay Conversation Section */}
      <div className="w-full flex flex-col gap-2">
        <div className="h-6 w-56 bg-bw-10 rounded-lg mb-2 animate-pulse" />
        <div className="h-16 w-full bg-bw-10 rounded-lg animate-pulse" />
      </div>

      {/* Submit Review Button */}
      <div className="w-full mt-8">
        <div className="h-12 w-full bg-bw-10 rounded-lg animate-pulse" />
      </div>
    </div>
  );
}
