export default function DashboardLoading() {
  return (
    <div className="flex flex-col gap-8 p-8">
      {/* Header */}
      <section className="flex items-center justify-between">
        <div className="h-8 w-32 bg-[var(--bw-10)] rounded-lg animate-pulse" />
        <div className="h-10 w-40 bg-[var(--bw-10)] rounded-lg animate-pulse" />
      </section>

      {/* Current Session */}
      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-36 bg-[var(--bw-10)] rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-[var(--bw-10)] rounded-lg animate-pulse" />
        </div>

        {/* Current Session Card */}
        <div className="border border-[var(--bw-20)] rounded-lg p-8 gap-8 flex flex-col">
          <div>
            <div className="h-7 w-48 bg-[var(--bw-10)] rounded-lg animate-pulse mb-2" />
            <div className="h-5 w-96 bg-[var(--bw-10)] rounded-lg animate-pulse" />
          </div>
          <div className="flex items-center gap-4">
            <div className="h-5 w-24 bg-[var(--bw-10)] rounded-lg animate-pulse" />
            <div className="h-2 w-full bg-[var(--bw-10)] rounded-full animate-pulse" />
          </div>
          <div className="h-10 w-full bg-[var(--bw-10)] rounded-lg animate-pulse" />
        </div>
      </section>

      {/* Stats Grid (2x2 on small, 1x4 on large screens) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="w-full aspect-[1/1] bg-[var(--bw-10)] rounded-lg flex flex-col items-center justify-center gap-2 animate-pulse"
          >
            <div className="h-16 w-24 bg-[var(--bw-20)] rounded-lg" />
            <div className="h-6 w-32 bg-[var(--bw-20)] rounded-lg" />
          </div>
        ))}
      </div>

      {/* Recent Training History */}
      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-48 bg-[var(--bw-10)] rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-[var(--bw-10)] rounded-lg animate-pulse" />
        </div>

        {/* History Item */}
        <div className="border border-[var(--bw-20)] rounded-lg p-8 flex items-center justify-between animate-pulse">
          <div className="flex flex-col gap-2">
            <div className="h-7 w-48 bg-[var(--bw-10)] rounded-lg" />
            <div className="h-5 w-96 bg-[var(--bw-10)] rounded-lg" />
          </div>
          <div className="flex flex-col justify-center text-center">
            <div className="h-5 w-24 bg-[var(--bw-10)] rounded-lg mb-1" />
            <div className="h-5 w-16 bg-[var(--bw-10)] rounded-lg" />
          </div>
        </div>
      </section>
    </div>
  );
}
