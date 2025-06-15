export default function PreparationPage() {
  return (
    <div className="flex flex-col gap-8">
      <div className="h-8 w-48 bg-bw-10 rounded-lg animate-pulse self-center" />

      <section className="flex flex-col gap-4 bg-marigold-5 border border-marigold-30 rounded-lg p-8 text-marigold-95">
        <div className="h-7 w-1/3 bg-marigold-10 rounded-lg animate-pulse" />
        <div className="h-5 w-full max-w-xl bg-marigold-10 rounded-lg animate-pulse" />
      </section>

      <div className="flex flex-col md:flex-row gap-4 items-stretch">
        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="h-7 w-1/4 bg-bw-10 rounded-lg animate-pulse" />
          <div className="flex flex-col gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="h-5 w-5 bg-bw-10 rounded animate-pulse mt-0.5" />
                <div className="h-5 w-full bg-bw-10 rounded-lg animate-pulse" />
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
          <div className="h-7 w-1/3 bg-bw-10 rounded-lg animate-pulse" />
          <div className="flex flex-col gap-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="h-5 w-5 bg-bw-10 rounded animate-pulse mt-0.5" />
                <div className="h-5 w-full bg-bw-10 rounded-lg animate-pulse" />
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="flex flex-col gap-4 w-full border border-bw-20 rounded-lg p-8">
        <div className="h-7 w-1/4 bg-bw-10 rounded-lg animate-pulse" />
        <div className="h-32 bg-bw-10 rounded-lg animate-pulse" />
      </section>

      <div className="flex gap-4">
        <div className="flex-1 h-10 bg-bw-10 rounded-lg animate-pulse" />
        <div className="flex-1 h-10 bg-bw-10 rounded-lg animate-pulse" />
      </div>
    </div>
  );
}
