import * as React from 'react';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from './Table';

export type ClickableTableColumn<T> = {
  header: React.ReactNode;
  accessor: keyof T | ((row: T) => React.ReactNode);
  className?: string;
  width?: string;
  align?: 'left' | 'right' | 'center';
  cell?: (row: T) => React.ReactNode;
};

export type ClickableTableProps<T> = {
  columns: ClickableTableColumn<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  rowKey?: (row: T) => React.Key;
  rowClassName?: (row: T) => string;
};

function getCellValue<T>(row: T, col: ClickableTableColumn<T>): React.ReactNode {
  if (col.cell) return col.cell(row);
  if (typeof col.accessor === 'function') return col.accessor(row);
  return (row as Record<string, unknown>)[col.accessor as string] as React.ReactNode;
}

export function ClickableTable<T>({
  columns,
  data,
  onRowClick,
  rowKey,
  rowClassName,
}: ClickableTableProps<T>) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((col, i) => (
            <TableHead
              key={i}
              className={col.className}
              style={col.width ? { width: col.width, minWidth: col.width } : undefined}
              align={col.align}
            >
              {col.header}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, i) => {
          const rowClass = rowClassName ? rowClassName(row) : '';
          const clickable = onRowClick ? 'cursor-pointer' : '';
          return (
            <TableRow
              key={rowKey ? rowKey(row) : i}
              className={`${clickable} ${rowClass}`.trim()}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
            >
              {columns.map((col, j) => (
                <TableCell
                  key={j}
                  className={col.className}
                  style={col.width ? { width: col.width, minWidth: col.width } : undefined}
                  align={col.align}
                >
                  {getCellValue(row, col)}
                </TableCell>
              ))}
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
