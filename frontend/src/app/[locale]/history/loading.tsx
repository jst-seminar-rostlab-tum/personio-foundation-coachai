import Link from 'next/link';

export default function HistoryPage() {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="text-xl font-bold text-gray-700">Training History</div>
        <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse" />
      </div>

      {/* Responsive Grid for Chart, Skills, Activity */}
      <div className="flex flex-col gap-8 md:grid md:grid-cols-4 md:gap-4 mb-8">
        {/* Performance Over Time Section */}
        <div className="md:col-span-2">
          <div className="text-lg font-bold text-gray-400 mb-4">Performance over time</div>
          <div className="w-full h-32 bg-gray-100 rounded flex items-end justify-center gap-2 p-4">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((_, i) => (
              <div
                key={i}
                className="bg-gray-300 animate-pulse rounded"
                style={{ height: `${40 + (i % 4) * 20}px`, width: '10px' }}
              />
            ))}
          </div>
        </div>
        {/* Skills Performance Section */}
        <div className="md:col-span-1.5">
          <div className="text-lg font-bold text-gray-400 mb-4">Skills Performance</div>
          {[1, 2, 3].map((_, i) => (
            <div key={i} className="mb-4">
              <div className="flex items-center justify-between mb-1">
                <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-10 bg-gray-200 rounded animate-pulse" />
              </div>
              <div className="w-full h-2 bg-gray-100 rounded">
                <div
                  className="h-2 bg-gray-300 rounded animate-pulse"
                  style={{ width: `${70 + i * 7}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        {/* Activity Section */}
        <div className="md:col-span-0.5">
          <div className="text-lg font-bold text-gray-400 mb-4">Activity</div>
          <div className="flex gap-2 md:grid md:grid-cols-2 md:grid-rows-2 md:gap-4 flex-row md:flex-col">
            {[1, 2, 3, 4].map((_, i) => (
              <div
                key={i}
                className="flex-1 min-w-0 bg-gray-100 rounded-lg shadow-md p-2 flex flex-col items-center animate-pulse"
              >
                <div className="h-4 md:h-2 w-6 sm:w-12 md:w-12 bg-gray-200 rounded mb-2" />
                <div className="h-8 md:h-4 w-8 sm:w-12 md:w-16 bg-gray-200 rounded" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 
      Previous Sessions Section 
      show 4 sessions on desktop and 2 on mobile
      */}
      <div className="w-full bg-gray-50 p-6 rounded-lg shadow-md mb-8">
        <div className="text-lg font-bold text-gray-400 mb-4">Previous Sessions</div>
        <div className="space-y-4">
          <div className="hidden lg:block">
            {[1, 2, 3, 4].map((_, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-gray-100 p-4 rounded-lg shadow mb-4"
              >
                <div className="h-6 w-40 bg-gray-200 rounded mb-2 animate-pulse" />
                <div className="flex items-center gap-2 ">
                  <Link href="/feedback/1">
                    <button className="h-8 bg-gray-200 ml-4 rounded-md px-2"> View</button>
                  </Link>
                  <div className="h-8 w-8 bg-gray-200 rounded-full ml-4" />
                </div>
              </div>
            ))}
          </div>
          <div className="lg:hidden">
            {[1, 2].map((_, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-gray-100 p-4 rounded-lg shadow mb-4"
              >
                <div className="h-6 w-40 bg-gray-200 rounded mb-2 animate-pulse" />
                <div className="flex items-center gap-2 ">
                  <Link href="/feedback/1">
                    <button className="h-8 bg-gray-200 ml-4 rounded-md px-2"> View</button>
                  </Link>
                  <div className="h-8 w-8 bg-gray-200 rounded-full ml-4" />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="text-center mt-4">
          <button className="text-gray-500 hover:text-gray-700">Load more sessions</button>
        </div>
      </div>

      <div className="w-full flex justify-center pb-8">
        <Link href="/dashboard" className="text-gray-400 hover:text-gray-500 text-sm underline">
          Return to dashboard
        </Link>
      </div>
    </div>
  );
}
