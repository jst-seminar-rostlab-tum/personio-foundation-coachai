/**
 * Shows a skeleton UI while preparation data loads.
 */
export default function PreparationPage() {
  return (
    <div className="flex flex-col gap-8 p-8">
      {/* Title */}
      <div className="h-8 w-80 bg-bw-40 rounded-lg self-center animate-pulse mb-4" />

      {/* 2x2 Grid for the 4 main boxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[...Array(4)].map((__, boxIdx) => (
          <section
            key={boxIdx}
            className="flex flex-col gap-4 w-full border border-bw-40 rounded-lg p-8 min-h-[220px]"
          >
            <div className="h-6 w-1/3 bg-bw-40 rounded-lg animate-pulse mb-2" />
            <div className="flex flex-col gap-3">
              {[...Array(4)].map((_, checklistIdx) => (
                <div key={checklistIdx} className="flex items-center gap-3">
                  <div className="h-5 w-5 bg-bw-40 rounded animate-pulse" />
                  <div className="h-5 w-full bg-bw-40 rounded-lg animate-pulse" />
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-4 mt-8">
        <div className="flex-1 h-12 bg-bw-40 rounded-lg animate-pulse" />
        <div className="flex-1 h-12 bg-bw-40 rounded-lg animate-pulse" />
      </div>
    </div>
  );
}
