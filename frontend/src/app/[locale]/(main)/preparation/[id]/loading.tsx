import React from 'react';

export default function PreparationPage() {
  return (
    <div className="flex flex-col gap-8 p-8">
      {/* Title */}
      <div className="h-8 w-48 bg-bw-10 rounded-lg self-center animate-pulse" />

      {/* Preparation Content */}
      <div className="flex flex-col gap-8">
        {/* Context Section */}
        <section className="flex flex-col gap-4 bg-marigold-5 border border-marigold-30 rounded-lg p-8">
          <div className="h-6 w-1/3 bg-marigold-10 rounded-lg animate-pulse" />
          <div className="h-5 w-full max-w-xl bg-marigold-10 rounded-lg animate-pulse" />
        </section>

        {/* Grid Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Objectives Section */}
          <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
            <div className="h-6 w-1/4 bg-bw-10 rounded-lg animate-pulse" />
            <div className="flex flex-col gap-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="h-5 w-5 bg-bw-10 rounded animate-pulse mt-0.5" />
                  <div className="h-5 w-full bg-bw-10 rounded-lg animate-pulse" />
                </div>
              ))}
            </div>
          </section>

          {/* Preparation Section */}
          <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
            <div className="h-6 w-1/3 bg-bw-10 rounded-lg animate-pulse" />
            <div className="flex flex-col gap-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="h-5 w-5 bg-bw-10 rounded animate-pulse mt-0.5" />
                  <div className="h-5 w-full bg-bw-10 rounded-lg animate-pulse" />
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      {/* Key Concepts Section */}
      <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
        <div className="h-6 w-1/4 bg-bw-10 rounded-lg animate-pulse" />
        <div className="flex flex-col gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="h-5 w-full bg-bw-10 rounded-lg animate-pulse" />
            </div>
          ))}
        </div>
      </section>

      {/* Resources Section */}
      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-48 bg-bw-10 rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-bw-10 rounded-lg animate-pulse" />
        </div>

        {[...Array(2)].map((_, i) => (
          <div
            key={i}
            className="border border-bw-20 rounded-lg p-8 flex items-center justify-between animate-pulse"
          >
            <div className="flex flex-col gap-2">
              <div className="h-7 w-48 bg-bw-10 rounded-lg" />
              <div className="h-5 w-96 bg-bw-10 rounded-lg" />
            </div>
            <div className="h-12 w-12 bg-bw-10 rounded-lg" />
          </div>
        ))}
      </section>

      {/* Navigation Buttons */}
      <div className="flex gap-4">
        <div className="flex-1 h-10 bg-bw-10 rounded-lg animate-pulse" />
        <div className="flex-1 h-10 bg-bw-10 rounded-lg animate-pulse" />
      </div>
    </div>
  );
}
