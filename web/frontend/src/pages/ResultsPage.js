import { useEffect, useState, useMemo } from 'react';
import { fetchAllResults } from '../api';
import ResultsTable from '../components/ResultsTable';

export default function ResultsPage() {
  const [allData, setAllData]       = useState([]);
  const [loading, setLoading]       = useState(true);
  const [selectedYears, setSelectedYears]   = useState(['All']);
  const [selectedGroups, setSelectedGroups] = useState(['All']);

  // Fetch entire dataset on mount
  useEffect(() => {
    fetchAllResults()
      .then(res => setAllData(Array.isArray(res.data) ? res.data : []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Derive dropdown options
  const years  = useMemo(() => Array.from(
                      new Set(allData.map(d => d['Draft Year']))
                    ).sort(), [allData]);
  const groups = useMemo(() => Array.from(
                      new Set(allData.map(d => d['Position Group']))
                    ).sort(), [allData]);

  // Handlers
  const onYearChange  = e =>
    setSelectedYears(Array.from(e.target.selectedOptions, o => o.value));
  const onGroupChange = e =>
    setSelectedGroups(Array.from(e.target.selectedOptions, o => o.value));

  // In-memory filtering
  const filteredData = useMemo(() => {
    return allData.filter(d => {
      const yearOK  = selectedYears.includes('All')  || selectedYears.includes(String(d['Draft Year']));
      const groupOK = selectedGroups.includes('All')|| selectedGroups.includes(d['Position Group']);
      return yearOK && groupOK;
    });
  }, [allData, selectedYears, selectedGroups]);

  if (loading) {
    return <div className="p-4">Loading…</div>;
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex space-x-6">
        {/* Draft Year multi-select */}
        <div>
          <label className="block font-medium mb-1">Draft Year</label>
          <select
            multiple
            size={Math.min(5, years.length + 1)}
            value={selectedYears}
            onChange={onYearChange}
            className="border p-1 rounded w-32"
          >
            <option value="All">All</option>
            {years.map(y => (
              <option key={y} value={String(y)}>
                {y}
              </option>
            ))}
          </select>
        </div>
        {/* Position Group multi-select */}
        <div>
          <label className="block font-medium mb-1">Position Group</label>
          <select
            multiple
            size={Math.min(5, groups.length + 1)}
            value={selectedGroups}
            onChange={onGroupChange}
            className="border p-1 rounded w-32"
          >
            <option value="All">All</option>
            {groups.map(g => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>
      </div>
      {/* Sortable table */}
      <ResultsTable data={filteredData} />
    </div>
  );
}
