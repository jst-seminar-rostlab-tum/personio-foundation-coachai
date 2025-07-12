'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Trash2 } from 'lucide-react';
import { ClickableTable, ClickableTableColumn } from '@/components/common/ClickableTable';
import { DeleteConfirmButton } from '@/components/common/DeleteConfirmButton';

const initialRows = [
  {
    id: 1,
    date: '2024-07-10T14:00:00',
    duration: 3897, // 1:04:57 in seconds
    performance: '92%',
  },
  {
    id: 2,
    date: '2024-07-08T09:30:00',
    duration: 1845, // 0:30:45 in seconds
    performance: '88%',
  },
  {
    id: 3,
    date: '2024-07-05T16:15:00',
    duration: 3600, // 1:00:00 in seconds
    performance: '-',
  },
];

export default function HistoryTable() {
  const router = useRouter();
  const [rows, setRows] = useState(initialRows);

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

  function formatDuration(seconds: number) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  const handleRowClick = () => router.push('/feedback/1');
  const handleDelete = (id: number) => {
    setRows((prev) => prev.filter((row) => row.id !== id));
  };

  const columns: ClickableTableColumn<(typeof initialRows)[number]>[] = [
    {
      header: 'Session Time',
      accessor: 'date',
      cell: (row) => formatDateTime(row.date),
    },
    {
      header: 'Duration',
      accessor: 'duration',
      className: 'text-right min-w-0 w-24',
      cell: (row) => formatDuration(row.duration),
      align: 'right',
    },
    {
      header: 'Performance',
      accessor: 'performance',
      className: 'text-right',
      align: 'right',
    },
    {
      header: '',
      accessor: () => '',
      className: 'text-right',
      cell: (row) => (
        <DeleteConfirmButton
          onConfirm={() => handleDelete(row.id)}
          namespace="History"
          className="text-bw-40 hover:text-flame-50 transition-colors cursor-pointer"
        >
          <Trash2 className="w-5 h-5" />
        </DeleteConfirmButton>
      ),
    },
  ];

  return (
    <ClickableTable
      columns={columns}
      data={rows}
      onRowClick={handleRowClick}
      rowKey={(row) => row.id}
    />
  );
}
