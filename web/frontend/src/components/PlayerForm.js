// PlayerForm.js
import React, { useState, useEffect } from 'react';
import { FEATURE_RANGES } from '../constants';

export default function PlayerForm({ onSubmit }) {
  const [playerName, setPlayerName] = useState('');
  const [position, setPosition]     = useState('Guards');
  const specs = FEATURE_RANGES[position];

  const [inputs, setInputs] = useState({});
  useEffect(() => {
    const init = {};
    Object.entries(specs).forEach(([f, cfg]) => init[f] = cfg.defaultValue);
    setInputs(init);
  }, [position, specs]);

  const handleChange = e => {
    const { name, value } = e.target;
    setInputs(prev => ({ ...prev, [name]: Number(value) }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit(position, inputs, playerName.trim() || null);
    setPlayerName('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block font-medium mb-1">Prospect Name</label>
          <input
            type="text"
            value={playerName}
            onChange={e => setPlayerName(e.target.value)}
            className="border p-2 rounded w-full"
            placeholder="Optional name"
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Position Group</label>
          <select
            value={position}
            onChange={e => setPosition(e.target.value)}
            className="border p-2 rounded w-full"
          >
            <option>Guards</option>
            <option>Wings</option>
            <option>Bigs</option>
          </select>
        </div>
      </div>

      <div className="max-h-64 overflow-y-auto space-y-4">
        {Object.entries(specs).map(([feature, cfg]) => {
          const raw = inputs[feature] ?? cfg.defaultValue;
          const display = feature === 'Height'
            ? `${Math.floor(raw/12)}′ ${raw%12}″`
            : raw.toFixed(1);

          return (
            <div key={feature}>
              <label className="block font-medium mb-1">
                {feature}: {display}
              </label>
              <input
                name={feature}
                type="range"
                min={cfg.min}
                max={cfg.max}
                step={(cfg.max - cfg.min) / 100}
                value={raw}
                onChange={handleChange}
                className="w-full"
              />
            </div>
          );
        })}
      </div>

      <button type="submit" className="btn-accent px-4 py-2">
        Create Player
      </button>
    </form>
  );
}
