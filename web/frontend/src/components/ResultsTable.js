import { useMemo, useEffect } from 'react';
import { useTable, useSortBy } from 'react-table';

export default function ResultsTable({ data }) {
  // 1) Define your columns
  const columns = useMemo(
    () => [
      { Header: 'Draft Year',    accessor: 'Draft Year' },
      { Header: 'Pick Number',   accessor: 'Pick Number' },
      { Header: 'Name',          accessor: 'Name' },
      { Header: 'Position Group',accessor: 'Position Group' },
      { Header: 'Predicted Score',accessor: 'Predicted Score' },
    ],
    []
  );

  // 2) Memoize data so react-table can detect changes
  const memoizedData = useMemo(() => data, [data]);

  // 3) Build the table instance with sort-by enabled
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    state: { sortBy },
  } = useTable(
    { columns, data: memoizedData },
    useSortBy
  );

  // 4) Debug: log sort state
  useEffect(() => {
    console.log('Current sortBy state:', sortBy);
  }, [sortBy]);

  return (
    <table {...getTableProps()} className="min-w-full bg-white">
      <thead>
        {headerGroups.map((hg, hi) => (
          <tr {...hg.getHeaderGroupProps()} key={hi}>
            {hg.headers.map((col, ci) => {
              const headerProps = col.getHeaderProps(col.getSortByToggleProps());
              return (
                <th
                  {...headerProps}
                  key={ci}
                  className="px-4 py-2 text-left font-semibold cursor-pointer"
                >
                  <div className="flex items-center">
                    {col.render('Header')}
                    {col.isSorted
                      ? col.isSortedDesc
                        ? ' 🔽'
                        : ' 🔼'
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
          // rely on row.getRowProps() for a unique key (row.id)
          return (
            <tr
              {...row.getRowProps()}
              className="hover:bg-gray-100"
            >
              {row.cells.map((cell, ci) => (
                <td
                  {...cell.getCellProps()}
                  key={ci}
                  className="border-t px-4 py-2"
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
