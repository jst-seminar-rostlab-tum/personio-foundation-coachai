export default function ConversationScenarioPageLoading() {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center mb-6">
        <div className="text-xl font-bold text-gray-400 text-center w-full sm:text-left">
          New Training Session
        </div>
      </div>
      {/* Stepper */}
      <div className="flex justify-between items-center mb-8 w-full mx-auto max-w-md">
        <div className="flex items-center w-full">
          <div className="w-10 h-10 rounded-full bg-gray-400 flex-shrink-0" />
          <div className="flex-1 h-1 bg-gray-300 mx-2" />
          <div className="w-10 h-10 rounded-full bg-gray-200 flex-shrink-0" />
          <div className="flex-1 h-1 bg-gray-300 mx-2" />
          <div className="w-10 h-10 rounded-full bg-gray-200 flex-shrink-0" />
        </div>
      </div>
      {/* 2-column grid with 4 square items */}
      <div className="grid grid-cols-2 gap-4 w-full mx-auto mb-8 md:max-w-lg xl:max-w-xl">
        {[1, 2, 3, 4].map((_, i) => (
          <div
            key={i}
            className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center animate-pulse"
          >
            <div className="w-2/3 h-2/3 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
      {/* Two full-width buttons on the same line */}
      <div className="flex gap-4 w-full md:max-w-lg xl:max-w-xl mx-auto">
        <button className="h-10 w-full bg-gray-100 rounded text-gray-500 font-semibold">
          Back
        </button>
        <button className="h-10 w-full bg-gray-300 text-gray-500 rounded font-semibold">
          Create Training{' '}
          <svg
            className="w-4 h-4 mb-0.5 inline-block ml-1"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
