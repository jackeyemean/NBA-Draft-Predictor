// frontend/src/pages/CreatePlayerPage.js
import { useState } from 'react';
import { fetchAllResults, predict } from '../api';
import ResultsTable from '../components/ResultsTable';
import { FEATURES_PG, FEATURES_WINGS, FEATURES_BIGS } from '../constants';

export default function CreatePlayerPage() {
  const [playerName, setPlayerName] = useState('');
  const [position, setPosition] = useState('PG');
  const [inputs, setInputs] = useState({});
  const [created, setCreated] = useState(null);
  const [comparison, setComparison] = useState([]);

  const featureSets = {
    PG: FEATURES_PG,
    Wings: FEATURES_WINGS,
    Bigs: FEATURES_BIGS,
  };
  const positionMap = {
    PG: 'Guard',
    Wings: 'Wing',
    Bigs: 'Big',
  };

  const handleChange = e =>
    setInputs({ ...inputs, [e.target.name]: parseFloat(e.target.value) });

  const handleSubmit = async e => {
    e.preventDefault();
    if (!playerName.trim()) {
      alert('Please enter a player name');
      return;
    }
    try {
      // 1) Predict new player
      const res = await predict({ ...inputs, 'Position Group': position });
      const newPlayer = {
        Name: playerName,
        'Draft Year': 2025,
        'Pick Number': '—',
        'Position Group': positionMap[position],
        'Predicted Score': res.data['Predicted Score'],
      };
      setCreated(newPlayer);

      // 2) Fetch all 2025 results and filter by same position group
      const all = await fetchAllResults();
      const arr = Array.isArray(all.data) ? all.data : [];
      setComparison(
        arr.filter(d => d['Position Group'] === positionMap[position])
      );
    } catch (err) {
      console.error(err);
      alert('Prediction failed');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Create Your Own Player</h1>
      <form onSubmit={handleSubmit} className="space-y-4 mb-6">
        <div>
          <label className="block font-medium mb-1">Name:</label>
          <input
            value={playerName}
            onChange={e => setPlayerName(e.target.value)}
            placeholder="Enter a name"
            required
            className="border p-2 w-full rounded"
          />
        </div>

        <div>
          <label className="block font-medium mb-1">
            Position Group:
          </label>
          <select
            value={position}
            onChange={e => setPosition(e.target.value)}
            className="border p-2 rounded"
          >
            <option value="PG">Guard</option>
            <option value="Wings">Wing</option>
            <option value="Bigs">Big</option>
          </select>
        </div>

        {featureSets[position].map((f, i) => (
          <div key={i}>
            <label className="block font-medium">
              {f}: {inputs[f] || 0}
            </label>
            <input
              name={f}
              type="range"
              min="0"
              max="100"
              step="0.1"
              value={inputs[f] || 0}
              onChange={handleChange}
              className="w-full"
            />
          </div>
        ))}

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Predict
        </button>
      </form>

      {created && (
        <>
          <h2 className="text-xl mb-2">Your Created Player</h2>
          <ResultsTable
            data={[created]}
            highlightName={playerName}
          />

          <h2 className="text-xl mt-6 mb-2">
            Comparison: {positionMap[position]}
          </h2>
          <ResultsTable
            data={comparison}
            highlightName={playerName}
          />
        </>
      )}
    </div>
);
}
