export default function OnboardingPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col items-center justify-between px-4 py-2">
        {/* Title skeleton */}
        <div className="w-3/4 h-8 mt-4 mb-2 text-2xl font-bold text-gray-400 text-center">
          Personalize Your Experience
        </div>
        <div className="w-1/2 h-4 bg-gray-100 rounded mb-3 animate-pulse" />
        {/* Steps skeleton */}
        <div className="flex gap-2 mb-4 w-full max-w-md justify-center">
          {[1, 2, 3].map((_, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-7 h-7 bg-gray-200 rounded-full animate-pulse mb-1" />
              <div className="w-10 h-2 bg-gray-100 rounded animate-pulse" />
            </div>
          ))}
        </div>
        {/* Question skeleton */}
        <div className="w-2/3 h-6 bg-gray-200 rounded mb-3 animate-pulse" />
        {/* Options skeleton */}
        <div className="w-full max-w-md space-y-2 mb-3">
          {[1, 2, 3, 4].map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gray-200 rounded-full animate-pulse" />
              <div className="flex-1 h-4 bg-gray-100 rounded animate-pulse" />
            </div>
          ))}
        </div>
        {/* Navigation buttons skeleton */}
        <div className="flex w-full max-w-md gap-2 mb-2">
          <div className="flex-1 h-9 bg-gray-100 rounded animate-pulse" />
          <div className="flex-1 h-9 bg-gray-200 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
