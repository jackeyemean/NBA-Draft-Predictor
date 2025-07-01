import React, { useEffect, useState, useMemo, useRef } from 'react';
import { fetchAllResults, predict } from '../api';
import PlayerForm from '../components/PlayerForm';
import ResultsTable from '../components/ResultsTable';

export default function ResultsPage() {
  const [histData, setHistData]           = useState([]);
  const [customPlayers, setCustomPlayers] = useState([]);
  const [formOpen, setFormOpen]           = useState(false);
  const [highlightName, setHighlightName] = useState(null);
  const tableRef = useRef(null);

  // load historical data once
  useEffect(() => {
    fetchAllResults()
      .then(res => setHistData(res.data || []))
      .catch(console.error);
  }, []);

  // create new player
  const handleCreate = async (code, inputs, name) => {
    try {
      const { data } = await predict({ ...inputs, 'Position Group': code });
      const pred  = data['Predicted Score'];
      const group =
        code === 'Guards' ? 'Guard' :
        code === 'Wings'  ? 'Wing'  : 'Big';
      const finalName = name || `Player ${customPlayers.length + 1}`;
      const newP = {
        Name: finalName,
        'Draft Year': 2025,
        'Pick Number': '—',
        'Position Group': group,
        'Predicted Score': pred
      };
      setCustomPlayers(prev => [newP, ...prev]);
      setHighlightName(finalName);
      setFormOpen(false);
    } catch (err) {
      console.error(err);
      alert('Prediction failed');
    }
  };

  // merge data
  const combined = useMemo(
    () => [...customPlayers, ...histData],
    [customPlayers, histData]
  );

  // filters — default year to 2025
  const [yearFilter, setYearFilter]   = useState('2025');
  const [groupFilter, setGroupFilter] = useState('All');

  const years  = useMemo(
    () => [...new Set(histData.map(d => d['Draft Year']))]
          .sort((a, b) => b - a)
          .map(String),
    [histData]
  );
  const groups = useMemo(
    () => [...new Set(histData.map(d => d['Position Group']))].sort(),
    [histData]
  );

  // filtered view (custom always shown)
  const filtered = useMemo(
    () => combined.filter(d => {
      const isCustom = customPlayers.some(p => p.Name === d.Name);
      const yearOK   = isCustom
        || yearFilter === 'All'
        || String(d['Draft Year']) === yearFilter;
      const groupOK  = groupFilter === 'All'
        || d['Position Group'] === groupFilter;
      return yearOK && groupOK;
    }),
    [combined, customPlayers, yearFilter, groupFilter]
  );

  // scroll to new
  useEffect(() => {
    if (!highlightName || !tableRef.current) return;
    const row = tableRef.current.querySelector(`tr[data-name="${highlightName}"]`);
    row?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [highlightName]);

  return (
    <div className="space-y-6">
      {/* Create New Player */}
      <section className="bg-white rounded shadow">
        <div
          onClick={() => setFormOpen(o => !o)}
          className="flex justify-between items-center p-4 border-b cursor-pointer hover:bg-gray-50"
        >
          <h2 className="text-xl font-semibold">Create New Player</h2>
          <span className="text-2xl">{formOpen ? '▲' : '▼'}</span>
        </div>
        {formOpen && (
          <div className="p-6">
            <PlayerForm onSubmit={handleCreate} />
          </div>
        )}
      </section>

      {/* Results (filters + table) */}
      <section className="bg-white rounded shadow p-6 space-y-4">
        <h2 className="text-xl font-semibold">Results</h2>

        {/* Filters */}
        <div className="flex items-end space-x-6">
          <div>
            <label className="block font-medium mb-1">Draft Year</label>
            <select
              value={yearFilter}
              onChange={e => setYearFilter(e.target.value)}
              className="border p-1 rounded"
            >
              <option>All</option>
              {years.map(y => (
                <option key={y}>{y}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block font-medium mb-1">Position Group</label>
            <select
              value={groupFilter}
              onChange={e => setGroupFilter(e.target.value)}
              className="border p-1 rounded"
            >
              <option>All</option>
              {groups.map(g => (
                <option key={g}>{g}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div ref={tableRef} className="overflow-y-auto max-h-[60vh]">
          <ResultsTable
            data={filtered}
            highlightNames={customPlayers.map(p => p.Name)}
          />
        </div>
      </section>
    </div>
  );
}
