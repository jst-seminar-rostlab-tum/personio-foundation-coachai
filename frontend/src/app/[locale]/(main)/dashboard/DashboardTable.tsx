'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Trash2 } from 'lucide-react';
import { ClickableTable, ClickableTableColumn } from '@/components/ui/ClickableTable';
import { DeleteConfirmButton } from '@/components/ui/DeleteConfirmButton';
import { Badge } from '@/components/ui/Badge';

function formatDateTime(dateString: string) {
  // Format as yyyy-MM-dd, HH:mm
  const date = new Date(dateString);
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}, ${hh}:${min}`;
}

const initialRows = [
  {
    id: 1,
    context: 'Giving Feedback',
    persona: 'Manager',
    difficulty: 'Hard',
    lastSession: '2024-07-10T14:00:00',
  },
  {
    id: 2,
    context: 'Conflict Resolution',
    persona: 'Colleague',
    difficulty: 'Medium',
    lastSession: '2024-07-08T09:30:00',
  },
  {
    id: 3,
    context: 'Active Listening',
    persona: 'Employee',
    difficulty: 'Easy',
    lastSession: '2024-07-05T16:15:00',
  },
];

export default function DashboardTable() {
  const router = useRouter();
  const [rows, setRows] = useState(initialRows);

  const handleRowClick = () => router.push('/history/1');
  const handleDelete = (id: number) => {
    setRows((prev) => prev.filter((row) => row.id !== id));
  };

  const columns: ClickableTableColumn<(typeof initialRows)[number]>[] = [
    {
      header: 'Situation',
      accessor: 'context',
    },
    {
      header: 'Other Party',
      accessor: 'persona',
    },
    {
      header: 'Difficulty',
      accessor: 'difficulty',
      cell: (row) => (
        <Badge difficulty={row.difficulty.toLowerCase() as 'easy' | 'medium' | 'hard'}>
          {row.difficulty}
        </Badge>
      ),
    },
    {
      header: 'Last Session',
      accessor: 'lastSession',
      cell: (row) => formatDateTime(row.lastSession),
    },
    {
      header: '',
      accessor: () => '',
      className: 'text-right',
      cell: (row) => (
        <DeleteConfirmButton
          onConfirm={() => handleDelete(row.id)}
          namespace="Dashboard"
          className="text-bw-40 hover:text-flame-50 transition-colors cursor-pointer"
        >
          <Trash2 className="w-5 h-5" />
        </DeleteConfirmButton>
      ),
    },
  ];

  return (
    <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
      <ClickableTable
        columns={columns}
        data={rows}
        onRowClick={handleRowClick}
        rowKey={(row) => row.id}
      />
    </div>
  );
}
