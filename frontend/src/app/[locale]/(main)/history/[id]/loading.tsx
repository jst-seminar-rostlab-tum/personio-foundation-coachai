/**
 * Shows a skeleton UI while scenario history loads.
 */
export default function HistoryPage() {
  return (
    <div className="flex flex-col gap-12">
      {/* History Header */}
      <div className="flex flex-col items-center md:items-start text-center md:text-left">
        <div className="h-8 w-48 bg-bw-40 rounded-lg animate-pulse mb-2" />
        <div className="h-5 w-64 bg-bw-40 rounded-lg animate-pulse" />
      </div>

      {/* History Stats */}
      <div className="w-full">
        <div className="w-full flex flex-col gap-6">
          {/* Skills Performance Section */}
          <div className="flex-1">
            <div className="h-6 w-48 bg-bw-40 rounded mb-4 animate-pulse" />
            <div className="flex flex-col gap-6 lg:grid lg:grid-cols-2 lg:gap-y-8 px-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <div className="h-4 w-24 bg-bw-40 rounded animate-pulse" />
                    <div className="h-4 w-10 bg-bw-40 rounded animate-pulse" />
                  </div>
                  <div className="w-full h-2 bg-bw-40 rounded">
                    <div
                      className="h-2 bg-bw-40 rounded animate-pulse"
                      style={{ width: `${70 + i * 7}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Section */}
          <div className="mt-10">
            <div className="h-6 w-24 bg-bw-40 rounded mb-4 animate-pulse" />
            <div className="flex flex-row gap-2 md:gap-6 min-w-0 overflow-x-auto">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="bg-bw-40 rounded-lg p-3 flex flex-col items-center animate-pulse w-full"
                >
                  <div className="h-4 w-10 bg-bw-40 rounded mb-1" />
                  <div className="h-3 w-16 bg-bw-40 rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Previous Sessions Section */}
      <div className="w-full">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2 gap-2 md:gap-0">
          <div className="h-6 w-48 bg-bw-40 rounded animate-pulse" />
          <div className="flex justify-between md:gap-6">
            <div className="h-8 w-32 bg-bw-40 rounded animate-pulse" />
            <div className="h-8 w-24 bg-bw-40 rounded animate-pulse" />
          </div>
        </div>
        <div className="flex flex-col gap-4">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="border border-bw-40 rounded-xl px-4 py-3 flex justify-between items-center animate-pulse"
            >
              <div>
                <div className="h-4 w-32 bg-bw-40 rounded mb-1" />
                <div className="h-3 w-48 bg-bw-40 rounded" />
              </div>
              <div className="text-xs text-bw-70 text-center whitespace-nowrap ml-4">
                <div className="h-3 w-8 bg-bw-40 rounded mb-1" />
                <div className="h-3 w-12 bg-bw-40 rounded" />
              </div>
            </div>
          ))}
        </div>
        <div className="flex justify-center mt-4">
          <div className="h-8 w-24 bg-bw-40 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
