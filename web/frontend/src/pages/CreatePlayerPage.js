// src/pages/CreatePlayerPage.js
import { useState } from 'react';
import { fetchAllResults, predict } from '../api';
import PlayerForm from '../components/PlayerForm';
import ResultsTable from '../components/ResultsTable';

export default function CreatePlayerPage() {
  const [custom, setCustom]       = useState([]);
  const [comparison, setComparison] = useState([]);

  const handleCreate = async (code, inputs) => {
    const res = await predict({
      ...inputs,
      'Position Group': code
    });
    const displayGroup = code === 'Guards' ? 'Guard' : code === 'Wings' ? 'Wing' : 'Bigs';
    const name = `Custom Player ${custom.length + 1}`;
    const newObj = {
      Name: name,
      'Draft Year': 2025,
      'Pick Number': '—',
      'Position Group': displayGroup,
      'Predicted Score': res.data['Predicted Score']
    };
    setCustom(prev => [newObj, ...prev]);

    const all = await fetchAllResults();
    const arr = Array.isArray(all.data) ? all.data : [];
    setComparison(arr.filter(d => d['Position Group'] === displayGroup));
  };

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold">Create Your Own Player</h1>
      <PlayerForm onSubmit={handleCreate} />

      {custom.length > 0 && (
        <>
          <h2 className="text-xl font-semibold">Your Players</h2>
          <ResultsTable data={custom} highlightName={custom[0].Name} />

          <h2 className="text-xl font-semibold mt-6">
            Historical Comparison ({custom[0]['Position Group']})
          </h2>
          <ResultsTable data={comparison} highlightName={custom[0].Name} />
        </>
      )}
    </div>
);
}
