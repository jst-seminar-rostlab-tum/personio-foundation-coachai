import Link from 'next/link';

export default function AdminLoadingPage() {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard">
          <button className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-gray-700 font-bold text-lg hover:bg-gray-300 transition-colors">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </Link>
        <div className="text-xl font-bold text-gray-700">Admin Dashboard</div>
      </div>
      {/* 2x2 Grid of Skeleton Cards */}
      <div className="grid grid-cols-2 gap-4 w-full mx-auto mb-8">
        {[1, 2, 3, 4].map((_, i) => (
          <div
            key={i}
            className="bg-gray-100 rounded-lg p-6 flex flex-col items-center animate-pulse"
          >
            <div className="h-8 w-16 bg-gray-200 rounded mb-2" />
            <div className="h-4 w-24 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
      {/* Skeleton Select */}
      <div className="w-full max-w-sm mb-8">
        <div className="h-10 bg-gray-100 rounded-lg animate-pulse" />
      </div>
      {/* Skeleton Accordions */}
      <div className="space-y-4 w-full mx-auto mb-8">
        {[1, 2, 3, 4].map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-lg shadow-md animate-pulse">
            {/* Accordion Header */}
            <div className="flex items-center justify-between p-4 cursor-pointer">
              <div className="h-5 w-32 bg-gray-200 rounded" />
              <div className="h-5 w-5 bg-gray-200 rounded-full" />
            </div>
            {/* Only the second accordion is open */}
            {i === 1 && (
              <div className="px-4 pb-4">
                <div className="h-12 w-full bg-gray-200 rounded mb-2" />
                <div className="h-20 w-2/3 bg-gray-200 rounded" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
