export default function DashboardLoading() {
  return (
    <div className="flex flex-col gap-12 p-8">
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <div className="h-8 w-32 bg-bw-10 rounded-lg animate-pulse" />
        <div className="h-10 w-full md:w-40 bg-bw-10 rounded-lg animate-pulse" />
      </section>

      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-36 bg-bw-10 rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-bw-10 rounded-lg animate-pulse" />
        </div>

        <div className="bg-marigold-5 border border-marigold-30 rounded-lg p-8 gap-8 flex flex-col">
          <div>
            <div className="h-7 w-48 bg-bw-10 rounded-lg animate-pulse mb-2" />
            <div className="h-5 w-96 bg-bw-10 rounded-lg animate-pulse" />
          </div>
          <div className="h-10 w-full bg-bw-10 rounded-lg animate-pulse" />
        </div>
      </section>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="@container w-full aspect-[1/1] bg-bw-10 rounded-lg flex flex-col items-center justify-center gap-2"
          >
            <div className="h-16 w-24 bg-bw-20 rounded-lg animate-pulse" />
            <div className="h-6 w-32 bg-bw-20 rounded-lg animate-pulse" />
          </div>
        ))}
      </div>

      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-48 bg-bw-10 rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-bw-10 rounded-lg animate-pulse" />
        </div>

        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="border border-bw-20 rounded-lg p-8 flex items-center justify-between animate-pulse"
          >
            <div className="flex flex-col gap-2">
              <div className="h-7 w-48 bg-bw-10 rounded-lg" />
              <div className="h-5 w-96 bg-bw-10 rounded-lg" />
            </div>
            <div className="flex flex-col justify-center text-center">
              <div className="h-5 w-24 bg-bw-10 rounded-lg mb-1" />
              <div className="h-5 w-16 bg-bw-10 rounded-lg" />
            </div>
          </div>
        ))}

        <div className="h-10 w-full bg-bw-10 rounded-lg animate-pulse" />
      </section>
    </div>
  );
}
