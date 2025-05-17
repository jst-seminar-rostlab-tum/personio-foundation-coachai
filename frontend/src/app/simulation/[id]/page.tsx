import Link from 'next/link';

export default function SimulationPage() {
  return <div>Simulation Page (placeholder)</div>;
}

  return (
    <div className="flex flex-col h-[92vh] justify-between">
      {/* Custom Header */}
      <div className="flex items-center justify-between mb-8 w-full gap-4">
        {/* Avatar */}
        <div className="w-12 h-12 bg-gray-200 rounded-full animate-pulse flex-shrink-0" />
        {/* Header and Subheading Skeleton */}
        <div className="flex flex-col flex-1 justify-center">
          <div className="h-5 w-32 bg-gray-200 rounded mb-2 animate-pulse" />
          <div className="h-4 w-24 bg-gray-100 rounded animate-pulse" />
        </div>
        {/* Right Side Placeholders */}
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <div className="h-4 w-16 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 w-10 bg-gray-100 rounded animate-pulse" />
        </div>
      </div>
      {/* Main Content Placeholder */}
      <div className="flex-1 flex items-center justify-center">
        <div className="w-full  h-full mb-10 bg-gray-100 rounded-lg animate-pulse" />
      </div>
      {/* Bottom Circle Buttons */}
      <div className="w-full flex justify-between items-center gap-4 px-4 pb-6 max-w-md mx-auto">
        {[1, 2, 3].map((_, i) => (
          <button key={i} className="w-14 h-14 bg-gray-200 rounded-full animate-pulse" />
        ))}
        <Link href="/feedback/1">
          <button className="w-14 h-14 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 pb-1 text-3xl hover:bg-gray-300 transition-colors">
            ×
          </button>
        </Link>
      </div>
    </div>
  );
}
