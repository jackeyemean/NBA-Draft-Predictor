import { useState } from 'react';
import { predict } from '../api';
import { FEATURES_PG, FEATURES_WINGS, FEATURES_BIGS } from '../constants';

export default function PlayerForm() {
  const [position, setPosition] = useState('PG');
  const [inputs, setInputs] = useState({});
  const [result, setResult] = useState(null);

  const featureSets = { PG: FEATURES_PG, Wings: FEATURES_WINGS, Bigs: FEATURES_BIGS };

  const handleChange = e => {
    setInputs({ ...inputs, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const payload = { ...inputs, 'Position Group': position };
    try {
      const res = await predict(payload);
      setResult(res.data['Predicted Score']);
    } catch {
      alert('Prediction failed');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block font-medium mb-1">Position Group:</label>
        <select
          value={position}
          onChange={e => setPosition(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="PG">Guards</option>
          <option value="Wings">Wings</option>
          <option value="Bigs">Bigs</option>
        </select>
      </div>

      {featureSets[position].map((f, i) => (
        <div key={i} className="space-y-1">
          <label className="block font-medium">
            {f}: {inputs[f] != null ? inputs[f] : '–'}
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

      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
        Predict
      </button>

      {result !== null && (
        <div className="mt-4 text-xl">Predicted Score: {result.toFixed(2)}</div>
      )}
    </form>
  );
}
