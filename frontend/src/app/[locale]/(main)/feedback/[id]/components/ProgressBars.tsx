import SegmentedProgress from '@/components/ui/SegmentedProgress';

interface ProgressBarItem {
  key: string;
  value: number;
}

interface ProgressBarsProps {
  data: ProgressBarItem[];
}

export default function ProgressBars({ data }: ProgressBarsProps) {
  return (
    <div className="flex flex-col gap-8 flex-1 w-full p-2">
      {data.map((item) => (
        <div key={item.key} className="flex flex-col">
          <div className="text-lg">
            <span>{item.key}</span>
          </div>
          <div className="flex justify-between items-center text-lg gap-4">
            <SegmentedProgress className="w-full" value={Math.round(item.value / 20)} />
            <span>{Math.round(item.value / 20)}/5</span>
          </div>
        </div>
      ))}
    </div>
  );
}
