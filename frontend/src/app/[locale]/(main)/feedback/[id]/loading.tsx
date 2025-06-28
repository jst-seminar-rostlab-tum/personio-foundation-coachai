import React from 'react';

export default function FeedbackDetailLoadingPage() {
  return (
    <div className="flex flex-col items-center gap-8">
      {/* Title */}
      <div className="h-8 w-48 bg-bw-10 rounded-lg animate-pulse" />

      {/* Session Info Banner */}
      <div className="h-20 bg-marigold-10 px-4 py-5 rounded-md text-center w-full">
        <div className="h-6 w-64 bg-marigold-20 rounded mb-2 mx-auto animate-pulse" />
        <div className="h-5 w-48 bg-marigold-20 rounded mx-auto animate-pulse" />
      </div>

      {/* Play Button Section */}
      <div className="h-10 w-32 bg-bw-10 rounded animate-pulse" />

      {/* Progress Bars and Score */}
      <div className="flex gap-3 items-center w-full justify-between">
        <div className="flex flex-col gap-4 p-2.5 flex-1">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex flex-col gap-2">
              <div className="flex justify-between text-base">
                <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
                <div className="h-4 w-8 bg-bw-10 rounded animate-pulse" />
              </div>
              <div className="w-full h-2 bg-bw-10 rounded">
                <div
                  className="h-2 bg-bw-20 rounded animate-pulse"
                  style={{ width: `${70 + i * 7}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="size-25 rounded-full bg-marigold-10 flex items-center justify-center">
          <div className="h-8 w-8 bg-marigold-20 rounded animate-pulse" />
        </div>
      </div>

      {/* Separator */}
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />

      {/* Stats Cards */}
      <div className="flex justify-evenly w-full">
        {[...Array(2)].map((_, i) => (
          <div className="flex gap-2 items-center" key={i}>
            <div className="rounded-full size-11 border-1 border-bw-30 bg-bw-10 flex items-center justify-center">
              <div className="h-5 w-5 bg-bw-20 rounded animate-pulse" />
            </div>
            <div className="flex flex-col gap-1 justify-between">
              <div className="h-4 w-20 bg-bw-10 rounded animate-pulse" />
              <div className="h-4 w-12 bg-bw-10 rounded animate-pulse" />
            </div>
          </div>
        ))}
      </div>

      {/* Separator */}
      <div className="my-4 mx-2 h-px w-full bg-bw-30" />

      {/* Listen Conversation Section */}
      <div className="flex items-center justify-center gap-3 mx-1 px-3 w-full h-20 bg-bw-10 rounded-md">
        <div className="size-11 rounded-full bg-marigold-50 flex items-center justify-center">
          <div className="h-5 w-5 bg-white rounded animate-pulse" />
        </div>
        <div className="flex flex-col justify-between flex-1">
          <div className="h-4 w-32 bg-bw-20 rounded animate-pulse" />
          <div className="flex gap-3 items-center">
            <div className="w-10 h-2 bg-bw-20 rounded animate-pulse" />
            <div className="flex gap-1 items-center">
              <div className="h-3 w-3 bg-bw-20 rounded animate-pulse" />
              <div className="h-3 w-8 bg-bw-20 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>

      {/* Accordions */}
      <div className="w-full space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border border-bw-20 rounded-lg animate-pulse">
            <div className="flex items-center justify-between p-4 cursor-pointer">
              <div className="h-5 w-32 bg-bw-10 rounded animate-pulse" />
              <div className="h-5 w-5 bg-bw-10 rounded-full animate-pulse" />
            </div>
            {i === 0 && (
              <div className="p-4">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="h-6 w-6 bg-bw-20 rounded animate-pulse" />
                    <div className="h-6 w-32 bg-bw-10 rounded animate-pulse" />
                  </div>
                  <div className="space-y-2 pl-4">
                    {[...Array(3)].map((__, j) => (
                      <div key={j} className="h-4 w-full bg-bw-10 rounded animate-pulse" />
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
