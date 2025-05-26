interface StatCardProps {
  value: string | number;
  label: string;
}

export default function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="w-full aspect-[1/1] bg-[var(--bw-10)] rounded-lg flex flex-col items-center justify-center gap-2">
      <p className="text-6xl font-bold">{value}</p>
      <p>{label}</p>
    </div>
  );
}
