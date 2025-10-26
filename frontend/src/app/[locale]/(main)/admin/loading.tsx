export default function AdminLoadingPage() {
  return (
    <div className="max-w-full">
      {/* Header */}
      <div className="text-2xl font-bold text-bw-70 text-center mb-2">
        <div className="h-8 w-48 bg-bw-40 rounded-lg mx-auto animate-pulse" />
      </div>
      <div className="text-sm text-bw-70 text-center mb-8">
        <div className="h-5 w-64 bg-bw-40 rounded-lg mx-auto animate-pulse" />
      </div>
      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[1, 2, 3, 4].map((_, i) => (
          <div key={i} className="bg-bw-40 rounded-lg p-6 flex flex-col items-center animate-pulse">
            <div className="h-8 w-16 bg-bw-40 rounded mb-2" />
            <div className="h-4 w-24 bg-bw-40 rounded" />
          </div>
        ))}
      </div>
      {/* Token Limit Input */}
      <div className="w-full max-w-md mb-8 text-left">
        <div className="h-4 w-32 bg-bw-40 rounded mb-2 animate-pulse" />
        <div className="flex gap-2 items-center">
          <div className="h-10 w-24 bg-bw-40 rounded animate-pulse" />
          <div className="h-10 w-20 bg-bw-40 rounded animate-pulse" />
        </div>
      </div>
      {/* Reviews Section Skeleton */}
      <div className="w-full mb-8">
        <div className="h-6 w-32 bg-bw-40 rounded mb-4 animate-pulse" />
        {[1, 2, 3, 4].map((_, i) => (
          <div key={i} className="flex flex-col md:flex-row gap-4 mb-4 animate-pulse">
            <div className="h-8 w-32 bg-bw-40 rounded mb-2" />
            <div className="h-5 w-64 bg-bw-40 rounded" />
          </div>
        ))}
      </div>
      {/* Accordions Skeleton */}
      <div className="w-full mt-8">
        {[1, 2, 3].map((_, i) => (
          <div key={i} className="mb-4 border border-bw-40 rounded-lg animate-pulse">
            <div className="flex items-center justify-between p-4 cursor-pointer">
              <div className="h-5 w-32 bg-bw-40 rounded" />
              <div className="h-5 w-5 bg-bw-40 rounded-full" />
            </div>
            {/* Only the first accordion is open for skeleton */}
            {i === 0 && (
              <div className="p-4">
                <div className="h-10 w-full bg-bw-40 rounded mb-2" />
                <div className="h-10 w-1/2 bg-bw-40 rounded" />
                <div className="h-10 w-1/3 bg-bw-40 rounded mt-2" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
