export default function ConversationScenarioPageLoading() {
  return (
    <div className="mx-auto pb-8">
      {/* New Training Session Title Skeleton */}
      <div className="h-10 w-96 bg-bw-10 rounded-lg mx-auto mb-8 animate-pulse" />

      {/* Stepper Skeleton - match real page width */}
      <div className="flex justify-center items-center mb-8 md:w-3/4 mx-auto">
        {/* Step 1 */}
        <div className="flex flex-col items-center">
          <div className="size-10 rounded-full bg-bw-10 animate-pulse flex items-center justify-center" />
        </div>
        <div className="h-1 w-32 bg-bw-10 mx-2" />
        {/* Step 2 */}
        <div className="flex flex-col items-center">
          <div className="size-10 rounded-full bg-bw-10 animate-pulse flex items-center justify-center" />
        </div>
        <div className="h-1 w-32 bg-bw-10 mx-2" />
        {/* Step 3 */}
        <div className="flex flex-col items-center">
          <div className="size-10 rounded-full bg-bw-10 animate-pulse flex items-center justify-center" />
        </div>
      </div>

      {/* Title Skeleton */}
      <div className="h-8 w-80 bg-bw-10 rounded-lg mx-auto mb-8 animate-pulse" />

      {/* Context selection cards - wider */}
      <div className="mb-10 w-full flex justify-center flex-col sm:flex-row gap-8">
        <div className="w-full md:w-2/5 box-border rounded-2xl bg-bw-10 animate-pulse flex flex-col items-start justify-center p-8 gap-4 min-h-[120px]" />
        <div className="w-full md:w-2/5 box-border rounded-2xl bg-bw-10 animate-pulse flex flex-col items-start justify-center p-8 gap-4 min-h-[120px]" />
      </div>

      {/* Next button bar - match real page width and padding */}
      <div className="fixed bottom-0 left-0 w-full z-50 bg-transparent">
        <div className="max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)] py-6">
          <div className="h-12 w-full bg-bw-10 rounded-lg animate-pulse" />
        </div>
      </div>
    </div>
  );
}
