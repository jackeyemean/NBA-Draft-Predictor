import React, { useState, useEffect } from 'react';
import { FEATURE_RANGES } from '../constants';

const LABELS = {
  'Age':            'Age',
  'Height':         'Height (ft & in)',
  'Weight':         'Weight (lbs)',
  'CT_Win%':        'College Win %',
  'CT_SOS':         'Strength of Schedule',
  'C_GS%':          'Games Started %',
  'C_MPG':          'MP',
  'C_USG%':         'Usage %',
  'C_FG%':          'FG%',
  'FGA_per_game':   'FGA',
  'C_3P%':          '3P%',
  '3PA_per_game':   '3PA',
  'C_FT%':          'FT %',
  'FTA_per_game':   'FTA',
  'AST_per_game':   'AST',
  'STL_per_game':   'STL',
  'TOV_per_game':   'TOV',
  'PPG':            'PTS',
  'OffReb':         'OFF REB',
  'DefReb':         'DEF REB',
  'BLK_per_game':   'BLK',
  'C_AST%':         'AST %',
  'C_BLK%':         'BLK %',
  'C_TOV%':         'TOV %',
  'C_TRB%':         'REB %',
  'C_OBPM':         'OBPM',
  'C_DBPM':         'DBPM',
  'C_BPM':          'BPM',
  'C_OWS':          'OWS',
  'C_DWS':          'DWS',
  'C_WS':           'WS'
};

const GROUPS = {
  'Guards': [
    ['Info',     ['Age','Height','Weight','CT_Win%','C_GS%','CT_SOS']],
    ['Advanced',    ['C_AST%','C_TOV%','C_USG%','C_OBPM','C_OWS']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_3P%','3PA_per_game','C_FT%','FTA_per_game']],
    ['Per Game',    ['C_MPG','PPG','AST_per_game','TOV_per_game','STL_per_game','OffReb','DefReb']]
  ],
  'Wings': [
    ['Info',     ['Age','Height','Weight','CT_Win%','C_GS%','CT_SOS']],
    ['Advanced',    ['C_AST%','C_TOV%','C_TRB%','C_USG%','C_BPM','C_WS']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_3P%','3PA_per_game','C_FT%','FTA_per_game']],
    ['Per Game',    ['C_MPG','PPG','AST_per_game','TOV_per_game','STL_per_game','OffReb','DefReb']]
  ],
  'Bigs': [
    ['Info',     ['Age','Height','Weight','CT_Win%','C_GS%','CT_SOS']],
    ['Advanced',    ['C_AST%','C_TOV%','C_BLK%','C_TRB%','C_USG%','C_DBPM','C_DWS']],
    ['Shooting',    ['C_FG%','FGA_per_game','C_FT%','FTA_per_game']],
    ['Per Game',    ['C_MPG','PPG','AST_per_game','TOV_per_game','STL_per_game','BLK_per_game','OffReb','DefReb']]
  ]
};

export default function PlayerForm({ onSubmit }) {
  const [name, setName]         = useState('');
  const [position, setPosition] = useState('Guards');
  const specs                   = FEATURE_RANGES[position];

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
      <div key={feature} className="flex flex-col mb-4">
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

  // split into left/right
  const allSections = GROUPS[position];
  const LEFT_KEYS = ['Info','Advanced'];
  const left  = allSections.filter(([sec]) => LEFT_KEYS.includes(sec));
  const right = allSections.filter(([sec]) => !LEFT_KEYS.includes(sec));

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

      {/* Two-column vertical stacks */}
      <div className="grid grid-cols-2 gap-8">
        <div>
          {left.map(([section, fields]) => (
            <section key={section} className="space-y-2 mb-6">
              <h3 className="font-semibold">{section}</h3>
              <div className="flex flex-col">
                {fields
                  .filter(f => f in specs)
                  .map(renderSlider)
                }
              </div>
            </section>
          ))}
        </div>

        <div>
          {right.map(([section, fields]) => (
            <section key={section} className="space-y-2 mb-6">
              <h3 className="font-semibold">{section}</h3>
              <div className="flex flex-col">
                {fields
                  .filter(f => f in specs)
                  .map(renderSlider)
                }
              </div>
            </section>
          ))}
        </div>
      </div>

      <button type="submit" className="btn-accent px-4 py-2">
        Create Player
      </button>
    </form>
  );
}
