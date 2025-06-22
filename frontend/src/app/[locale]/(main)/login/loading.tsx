import React from 'react';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md border border-bw-20">
          {/* Card Header */}
          <div className="p-6 border-b border-bw-20">
            <div className="h-6 w-32 bg-bw-10 rounded mb-2 animate-pulse" />
            <div className="h-4 w-48 bg-bw-10 rounded animate-pulse" />
          </div>

          {/* Card Content */}
          <div className="p-6">
            {/* Tabs */}
            <div className="flex mb-6">
              <div className="flex-1 h-10 bg-bw-20 rounded-l animate-pulse" />
              <div className="flex-1 h-10 bg-bw-10 rounded-r animate-pulse" />
            </div>

            {/* Tab Content */}
            <div className="space-y-4">
              <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
              <div className="h-4 w-20 bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-20 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
