interface StatCardProps {
  value: string | number;
  label: string;
}

export default function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="@container w-full bg-bw-10 rounded-lg flex flex-col justify-center gap-2 p-4 md:p-6">
      <p className="text-base md:text-lg text-bw-40">{label}</p>
      <p className="bebas-neue text-4xl md:text-6xl">{value}</p>
    </div>
  );
}
