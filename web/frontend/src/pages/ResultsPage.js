// src/pages/ResultsPage.js
import { useEffect, useState, useMemo } from 'react';
import { fetchAllResults } from '../api';
import ResultsTable from '../components/ResultsTable';

export default function ResultsPage() {
  const [allData, setAllData]             = useState([]);
  const [loading, setLoading]             = useState(true);
  const [viewAll, setViewAll]             = useState(true);
  const [yearFilter, setYearFilter]       = useState(null);
  const [groupFilter, setGroupFilter]     = useState('All');

  useEffect(() => {
    fetchAllResults()
      .then(res => setAllData(res.data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const years = useMemo(() => Array.from(
    new Set(allData.map(d => d['Draft Year']))
  ).sort((a,b)=>b-a), [allData]);

  const groups = useMemo(() => Array.from(
    new Set(allData.map(d => d['Position Group']))
  ).sort(), [allData]);

  const filtered = useMemo(() => {
    return allData
      .filter(d => {
        if (!viewAll && yearFilter != null && d['Draft Year'] !== yearFilter)
          return false;
        if (groupFilter !== 'All' && d['Position Group'] !== groupFilter)
          return false;
        return true;
      })
      .sort((a,b) => b['Draft Year'] - a['Draft Year']);
  }, [allData, viewAll, yearFilter, groupFilter]);

  if (loading) return <div className="p-4">Loading…</div>;

  return (
    <div className="p-4 space-y-6">
      <div className="flex flex-wrap items-center gap-6">
        {/* All Classes Toggle */}
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={viewAll}
            onChange={() => setViewAll(v => !v)}
            className="h-5 w-5 text-orange-500"
          />
          <span className="font-medium">All Draft Classes</span>
        </label>

        {/* Year picker */}
        {!viewAll && (
          <div>
            <label className="block font-medium mb-1">Draft Year</label>
            <select
              value={yearFilter ?? ''}
              onChange={e => setYearFilter(Number(e.target.value))}
              className="border p-2 rounded"
            >
              <option value="">Select Year</option>
              {years.map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
        )}

        {/* Position picker */}
        <div>
          <label className="block font-medium mb-1">Position Group</label>
          <select
            value={groupFilter}
            onChange={e => setGroupFilter(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="All">All</option>
            {groups.map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>
      </div>

      <ResultsTable data={filtered} />
    </div>
  );
}
