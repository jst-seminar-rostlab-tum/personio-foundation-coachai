interface StatCardProps {
  value: string | number;
  label: string;
}

export default function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="@container w-full bg-white rounded-lg flex flex-col justify-center gap-3 p-4 md:p-6">
      <p className="text-base md:text-md font-normal text-bw-70">{label}</p>
      <p className="bebas-neue text-4xl md:text-6xl">{value}</p>
    </div>
  );
}
