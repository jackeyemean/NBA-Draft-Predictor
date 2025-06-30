// src/components/PlayerForm.js
import React, { useState, useEffect } from 'react';
import { FEATURE_RANGES } from '../constants';

export default function PlayerForm({ onSubmit }) {
  // Use "Guards" as the initial position code
  const [position, setPosition] = useState('Guards');
  const specs = FEATURE_RANGES[position];

  // Initialize all inputs from the defaultValue for each feature
  const [inputs, setInputs] = useState(() => {
    const init = {};
    Object.entries(specs).forEach(([feature, cfg]) => {
      init[feature] = cfg.defaultValue;
    });
    return init;
  });

  // Whenever the position changes, reset inputs back to that position’s defaults
  useEffect(() => {
    const init = {};
    Object.entries(FEATURE_RANGES[position]).forEach(([feature, cfg]) => {
      init[feature] = cfg.defaultValue;
    });
    setInputs(init);
  }, [position]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInputs((prev) => ({
      ...prev,
      [name]: parseFloat(value),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(position, inputs);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block font-medium mb-1">Position Group</label>
        <select
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="Guards">Guards</option>
          <option value="Wings">Wings</option>
          <option value="Bigs">Bigs</option>
        </select>
      </div>

      {Object.entries(specs).map(([feature, cfg]) => {
        // Use the input value if defined, otherwise defaultValue
        const value = inputs[feature] !== undefined
          ? inputs[feature]
          : cfg.defaultValue;
        return (
          <div key={feature} className="space-y-1">
            <label className="block font-medium">
              {feature}: {value.toFixed(1)}
            </label>
            <input
              name={feature}
              type="range"
              min={cfg.min}
              max={cfg.max}
              step={(cfg.max - cfg.min) / 100}
              value={value}
              onChange={handleChange}
              className="w-full"
            />
          </div>
        );
      })}

      <button type="submit" className="btn-accent px-4 py-2">
        Predict
      </button>
    </form>
  );
}
