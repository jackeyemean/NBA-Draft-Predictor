// src/components/ResultsTable.js
import { useMemo, useEffect } from 'react';
import { useTable, useSortBy } from 'react-table';

export default function ResultsTable({ data, highlightName }) {
  const columns = useMemo(
    () => [
      { Header: 'Draft Year',    accessor: 'Draft Year' },
      { Header: 'Pick #',        accessor: 'Pick Number' },
      { Header: 'Name',          accessor: 'Name' },
      { Header: 'Position',      accessor: 'Position Group' },
      { Header: 'Pred Score',    accessor: 'Predicted Score' },
    ],
    []
  );

  const memoData = useMemo(() => data, [data]);
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state: { sortBy },
  } = useTable({ columns, data: memoData }, useSortBy);

  useEffect(() => console.log('sortBy ➔', sortBy), [sortBy]);

  return (
    <table
      {...getTableProps()}
      className="w-full table-auto bg-white shadow-sm"
    >
      <thead className="bg-blue-100">
        {headerGroups.map((hg, hi) => (
          <tr {...hg.getHeaderGroupProps()} key={hi}>
            {hg.headers.map((col, ci) => {
              const hProps = col.getHeaderProps(col.getSortByToggleProps());
              return (
                <th
                  {...hProps}
                  key={ci}
                  className="px-3 py-2 text-left text-sm font-bold text-blue-900 cursor-pointer"
                >
                  <div className="flex items-center space-x-1">
                    <span>{col.render('Header')}</span>
                    {col.isSorted
                      ? col.isSortedDesc
                        ? '🔽'
                        : '🔼'
                      : ''}
                  </div>
                </th>
              );
            })}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map(row => {
          prepareRow(row);
          const isNew = highlightName === row.original.Name;
          return (
            <tr
              {...row.getRowProps()}
              className={`even:bg-gray-50 hover:bg-gray-100 ${
                isNew ? 'bg-orange-100' : ''
              }`}
            >
              {row.cells.map((cell, ci) => (
                <td
                  {...cell.getCellProps()}
                  key={ci}
                  className="px-3 py-2 text-sm"
                >
                  {cell.render('Cell')}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
