import React from 'react';

export interface Column<T> {
  header: string;
  accessor: keyof T | ((row: T) => React.ReactNode);
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField: keyof T;
  isLoading?: boolean;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  className?: string;
}

function Table<T>({
  columns,
  data,
  keyField,
  isLoading = false,
  onRowClick,
  emptyMessage = 'No data available',
  className = '',
}: TableProps<T>) {
  // Table skeleton loader
  const TableSkeleton = () => (
    <tbody>
      {Array.from({ length: 5 }).map((_, index) => (
        <tr key={index} className="animate-pulse">
          {columns.map((column, colIndex) => (
            <td key={colIndex} className="px-6 py-4 whitespace-nowrap">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  );

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-700">
          <tr>
            {columns.map((column, index) => (
              <th
                key={index}
                scope="col"
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider ${column.className || ''}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>

        {isLoading ? (
          <TableSkeleton />
        ) : data.length > 0 ? (
          <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
            {data.map(row => (
              <tr
                key={String(row[keyField])}
                className={`
                  ${onRowClick ? 'cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700' : ''}
                `}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map((column, colIndex) => {
                  const cellValue = typeof column.accessor === 'function'
                    ? column.accessor(row)
                    : row[column.accessor];

                  return (
                    <td key={colIndex} className="px-6 py-4 whitespace-nowrap">
                      {cellValue}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        ) : (
          <tbody className="bg-white dark:bg-gray-800">
            <tr>
              <td
                colSpan={columns.length}
                className="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
              >
                {emptyMessage}
              </td>
            </tr>
          </tbody>
        )}
      </table>
    </div>
  );
}

export default Table;