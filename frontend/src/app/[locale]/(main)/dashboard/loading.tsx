import React from 'react';

export default function DashboardLoading() {
  return (
    <div className="flex flex-col gap-12">
      {/* Header Section */}
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <div className="h-8 w-64 bg-bw-10 rounded-lg animate-pulse" />
        <div className="h-10 w-full md:w-40 bg-bw-10 rounded-lg animate-pulse" />
      </section>

      {/* Dashboard Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="@container w-full aspect-[2/1] bg-bw-10 rounded-lg flex flex-col justify-center p-8 gap-2"
          >
            <div className="h-6 w-24 bg-bw-20 rounded-lg animate-pulse" />
            <div className="h-16 w-32 bg-bw-20 rounded-lg animate-pulse" />
          </div>
        ))}
      </div>

      {/* Recent Sessions Section */}
      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-48 bg-bw-10 rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-bw-10 rounded-lg animate-pulse" />
        </div>

        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="border border-bw-20 rounded-lg p-8 flex items-center justify-between animate-pulse"
          >
            <div className="flex flex-col gap-2">
              <div className="h-7 w-48 bg-bw-10 rounded-lg" />
              <div className="h-5 w-96 bg-bw-10 rounded-lg" />
            </div>
            <div className="flex flex-col justify-center text-center">
              <div className="h-5 w-24 bg-bw-10 rounded-lg mb-1" />
              <div className="h-5 w-16 bg-bw-10 rounded-lg" />
            </div>
          </div>
        ))}

        <div className="h-10 w-full bg-bw-10 rounded-lg animate-pulse" />
      </section>
    </div>
  );
}
