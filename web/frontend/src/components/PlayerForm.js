// src/components/PlayerForm.js
import React, { useState, useEffect } from 'react';
import { FEATURE_RANGES } from '../constants';

const LABELS = {
  'Age':            'Age',
  'Height':         'Height (ft/in)',
  'Weight':         'Weight (lbs)',
  'CT_Win%':        'College Win %',
  'CT_SOS':         'Strength of Schedule',
  'C_GS%':          'Games Started %',
  'C_MPG':          'Minutes/Game',
  'C_USG%':         'Usage %',
  'C_FG%':          'Field Goal %',
  'FGA_per_game':   'FGA/Game',
  'C_3P%':          '3-Point %',
  '3PA_per_game':   '3PA/Game',
  'C_FT%':          'Free Throw %',
  'FTA_per_game':   'FTA/Game',
  'AST_per_game':   'Assists/Game',
  'STL_per_game':   'Steals/Game',
  'TOV_per_game':   'Turnovers/Game',
  'PPG':            'Points/Game',
  'OffReb':         'Offensive Reb/Game',
  'DefReb':         'Defensive Reb/Game',
  'BLK_per_game':   'Blocks/Game',
  'C_AST%':         'Assist %',
  'C_TOV%':         'Turnover %',
  'C_TS%':          'True Shooting %',
  'C_AST_TO':       'AST/TO Ratio',
  'C_ORB_DRB':      'ORB/DRB Ratio',
  'C_TRB%':         'Rebound %',
  'C_OBPM':         'Offensive BPM',
  'C_DBPM':         'Defensive BPM',
  'C_BPM':          'Box Plus/Minus',
  'C_OWS':          'Offensive WS',
  'C_DWS':          'Defensive WS',
  'C_WS':           'Win Shares'
};

const GROUPS = {
  'Guards': [
    ['Profile',     ['Age','Height','Weight']],
    ['College',     ['CT_Win%','CT_SOS']],
    ['Usage',       ['C_GS%','C_MPG','C_USG%']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_3P%','3PA_per_game','C_FT%','FTA_per_game']],
    ['Counting',    ['AST_per_game','STL_per_game','TOV_per_game','PPG']],
    ['Rebounds',    ['OffReb','DefReb']],
    ['Percentages', ['C_AST%','C_TOV%']],
    ['Box',         ['C_OBPM','C_OWS']]
  ],
  'Wings': [
    ['Profile',     ['Age','Height','Weight']],
    ['College',     ['CT_Win%','CT_SOS']],
    ['Usage',       ['C_GS%','C_MPG','C_USG%']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_3P%','3PA_per_game','C_FT%','FTA_per_game']],
    ['Counting',    ['AST_per_game','STL_per_game','TOV_per_game','PPG']],
    ['Rebounds',    ['OffReb','DefReb']],
    ['Percentages', ['C_AST%','C_TOV%']],
    ['Box',         ['C_OBPM','C_DBPM','C_BPM','C_OWS','C_DWS','C_WS']]
  ],
  'Bigs': [
    ['Profile',     ['Age','Height','Weight']],
    ['College',     ['CT_Win%','CT_SOS']],
    ['Usage',       ['C_GS%','C_MPG','C_USG%']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_3P%','3PA_per_game','C_FT%','FTA_per_game']],
    ['Counting',    ['AST_per_game','STL_per_game','TOV_per_game','PPG','BLK_per_game']],
    ['Rebounds',    ['OffReb','DefReb']],
    ['Percentages', ['C_AST%','C_TOV%','C_BLK%','C_TRB%']],
    ['Box',         ['C_OBPM','C_DBPM','C_BPM','C_OWS','C_DWS','C_WS']]
  ]
};

export default function PlayerForm({ onSubmit }) {
  const [name, setName]         = useState('');
  const [position, setPosition] = useState('Guards');
  const specs                   = FEATURE_RANGES[position];

  // initialize/reset inputs on position change
  const [inputs, setInputs] = useState({});
  useEffect(() => {
    const init = {};
    Object.entries(specs).forEach(([k, cfg]) => init[k] = cfg.defaultValue);
    setInputs(init);
  }, [position, specs]);

  const handleChange = e => {
    const { name, value } = e.target;
    setInputs(prev => ({ ...prev, [name]: Number(value) }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit(position, inputs, name.trim() || null);
    setName('');
  };

  const renderSlider = feature => {
    const cfg = specs[feature];
    const raw = inputs[feature] ?? cfg.defaultValue;
    const display = feature === 'Height'
      ? `${Math.floor(raw/12)}′ ${raw % 12}″`
      : raw.toFixed(1);

    return (
      <div key={feature} className="flex flex-col">
        <label htmlFor={feature} className="font-medium mb-1" title={LABELS[feature]}>
          {LABELS[feature]}: {display}
        </label>
        <input
          id={feature}
          name={feature}
          type="range"
          min={cfg.min}
          max={cfg.max}
          step={(cfg.max - cfg.min) / 100 || 1}
          value={raw}
          onChange={handleChange}
          className="w-full"
        />
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name & Position */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block font-medium mb-1">Prospect Name</label>
          <input
            type="text"
            className="border p-2 rounded w-full"
            placeholder="Optional"
            value={name}
            onChange={e => setName(e.target.value)}
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Position Group</label>
          <select
            className="border p-2 rounded w-full"
            value={position}
            onChange={e => setPosition(e.target.value)}
          >
            <option>Guards</option>
            <option>Wings</option>
            <option>Bigs</option>
          </select>
        </div>
      </div>

      {/* Slider Sections */}
      {GROUPS[position].map(([section, fields]) => (
        <section key={section}>
          <h3 className="font-semibold mb-2">{section}</h3>
          <div className="grid grid-cols-2 gap-4">
            {fields.map(renderSlider)}
          </div>
        </section>
      ))}

      <button type="submit" className="btn-accent px-4 py-2">
        Create Player
      </button>
    </form>
  );
}
