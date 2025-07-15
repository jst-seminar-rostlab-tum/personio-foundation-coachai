export default function OnboardingPage() {
  return (
    <div className="flex flex-col items-center w-full min-h-screen pt-8">
      {/* Main Content */}
      <div className="flex flex-col items-center w-full gap-8">
        {/* Title and Subtitle */}
        <div className="flex flex-col gap-2 text-center mb-2">
          <div className="h-8 w-[36rem] bg-bw-10 rounded-lg mx-auto animate-pulse" />
          <div className="h-5 w-[28rem] bg-bw-10 rounded-lg mx-auto animate-pulse" />
        </div>

        {/* Stepper */}
        <div className="flex items-center justify-center w-full gap-0 mb-8">
          <div className="w-10 h-10 bg-bw-20 rounded-full animate-pulse mr-2" />
          <div className="h-1 w-40 bg-bw-10 animate-pulse" />
          <div className="w-10 h-10 bg-bw-10 rounded-full animate-pulse mx-2" />
          <div className="h-1 w-40 bg-bw-10 animate-pulse" />
          <div className="w-10 h-10 bg-bw-10 rounded-full animate-pulse ml-2" />
        </div>

        {/* Question */}
        <div className="h-7 w-[32rem] bg-bw-10 rounded-lg mx-auto mb-4 animate-pulse" />

        {/* Options */}
        <div className="w-full max-w-2xl flex flex-col gap-6 mb-8">
          {[1, 2, 3, 4].map((_, i) => (
            <div key={i} className="flex items-start gap-4">
              <div className="w-6 h-6 bg-bw-10 rounded-full animate-pulse mt-1" />
              <div className="flex flex-col gap-2 flex-1">
                <div className="h-5 w-72 bg-bw-10 rounded animate-pulse" />
                <div className="h-4 w-96 bg-bw-10 rounded animate-pulse" />
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Buttons */}
        <div className="w-full max-w-2xl flex gap-4 mb-2">
          <div className="flex-1 h-12 bg-bw-10 rounded-lg animate-pulse" />
        </div>
        {/* Skip Link */}
        <div className="w-full max-w-2xl flex justify-center">
          <div className="h-5 w-24 bg-bw-10 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}
