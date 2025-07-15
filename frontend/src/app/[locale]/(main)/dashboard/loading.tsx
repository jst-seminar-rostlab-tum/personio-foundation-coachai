export default function DashboardLoading() {
  return (
    <div className="flex flex-col gap-12">
      {/* Header Section */}
      <section className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 md:gap-0">
        <div className="h-8 w-64 bg-bw-10 rounded-lg animate-pulse" />
        <div className="h-10 w-full md:w-40 bg-bw-10 rounded-lg animate-pulse" />
      </section>

      {/* Dashboard Stats Grid (4 cards only) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="@container w-full aspect-[2/1] bg-bw-10 rounded-lg flex flex-col justify-center p-8 gap-2"
          >
            <div className="h-6 w-24 bg-bw-20 rounded-lg animate-pulse" />
            <div className="h-16 w-32 bg-bw-20 rounded-lg animate-pulse" />
          </div>
        ))}
      </div>

      {/* Recent Sessions Section */}
      <section className="flex flex-col gap-4">
        <div>
          <div className="h-7 w-48 bg-bw-10 rounded-lg animate-pulse mb-2" />
          <div className="h-5 w-64 bg-bw-10 rounded-lg animate-pulse" />
        </div>
        {/* Table placeholder skeleton with 3 columns */}
        <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
          <table className="min-w-full divide-y divide-bw-20">
            <thead>
              <tr>
                <th className="px-6 py-3">
                  <div className="h-5 w-32 bg-bw-10 rounded animate-pulse" />
                </th>
                <th className="px-6 py-3">
                  <div className="h-5 w-24 bg-bw-10 rounded animate-pulse" />
                </th>
                <th className="px-6 py-3">
                  <div className="h-5 w-20 bg-bw-10 rounded animate-pulse" />
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bw-20">
              {[...Array(3)].map((_, i) => (
                <tr key={i}>
                  <td className="px-6 py-4">
                    <div className="h-5 w-48 bg-bw-10 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-5 w-24 bg-bw-10 rounded animate-pulse" />
                  </td>
                  <td className="px-6 py-4">
                    <div className="h-5 w-20 bg-bw-10 rounded animate-pulse" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
