import React, { useMemo } from 'react';
import { useTable, useSortBy } from 'react-table';

export default function ResultsTable({
  data,
  highlightNames = [],
  defaultSort = [{ id: 'Predicted Score', desc: true }]
}) {
  const columns = useMemo(
    () => [
      { Header: 'Draft Year',      accessor: 'Draft Year' },
      { Header: 'Pick Number',     accessor: 'Pick Number' },
      { Header: 'Name',            accessor: 'Name' },
      { Header: 'Position',        accessor: 'Position Group' },
      {
        Header: 'Predicted Score',
        accessor: 'Predicted Score',
        // numeric sort so 4.962 > 4.99, etc.
        sortType: (rowA, rowB, columnId) =>
          rowA.values[columnId] - rowB.values[columnId]
      },
    ],
    []
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow
  } = useTable(
    { columns, data, initialState: { sortBy: defaultSort } },
    useSortBy
  );

  return (
    <div className="overflow-y-auto">
      <table {...getTableProps()} className="min-w-full border-collapse">
        <thead>
          {headerGroups.map((hg, i) => (
            <tr {...hg.getHeaderGroupProps()} key={i}>
              {hg.headers.map((col, j) => (
                <th
                  {...col.getHeaderProps(col.getSortByToggleProps())}
                  key={j}
                  className="sticky top-0 bg-white px-3 py-2 text-left font-bold border-b"
                >
                  <div className="flex items-center space-x-1">
                    {col.render('Header')}
                    <span className="text-xs">
                      {col.isSorted
                        ? col.isSortedDesc
                          ? '↓'
                          : '↑'
                        : ''}
                    </span>
                  </div>
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row);
            const name = row.original.Name;
            const isCustom = highlightNames.includes(name);
            return (
              <tr
                {...row.getRowProps()}
                data-name={name}
                className={`border-b ${isCustom ? 'bg-orange-100' : ''}`}
              >
                {row.cells.map((cell, k) => (
                  <td
                    {...cell.getCellProps()}
                    key={k}
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
    </div>
  );
}
