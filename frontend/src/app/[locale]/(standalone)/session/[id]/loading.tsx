export default function SessionPage() {
  return (
    <div className="flex flex-col h-[92vh] justify-between">
      {/* Custom Header */}
      <div className="flex items-center justify-between mb-8 w-full gap-4">
        <div className="w-12 h-12 bg-gray-200 rounded-full animate-pulse flex-shrink-0" />
        <div className="flex flex-col flex-1 justify-center">
          <div className="h-5 w-32 bg-gray-200 rounded mb-2 animate-pulse" />
          <div className="h-4 w-24 bg-gray-100 rounded animate-pulse" />
        </div>
        <div className="flex flex-col items-end gap-2 flex-shrink-0">
          <div className="h-4 w-16 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 w-10 bg-gray-100 rounded animate-pulse" />
        </div>
      </div>
      {/* Main Content Placeholder */}
      <div className="flex-1 flex items-center justify-center">
        <div className="w-full h-full mb-10 bg-gray-100 rounded-lg animate-pulse" />
      </div>
      {/* Bottom Circle Buttons */}
      <div className="w-full flex justify-between items-center gap-4 px-4 pb-6 max-w-md mx-auto">
        {[1, 2, 3].map((_, i) => (
          <div key={i} className="w-14 h-14 bg-gray-200 rounded-full animate-pulse" />
        ))}
        <div className="w-14 h-14 bg-gray-200 rounded-full animate-pulse" />
      </div>
    </div>
  );
}
