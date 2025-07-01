# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
from models import models

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000","http://127.0.0.1:3000"]}})

# Load and sanitize results.csv
df = pd.read_csv(Path(__file__).parent / 'results.csv')
df = df.replace({np.nan: None})

@app.route('/api/results')
def get_results():
    year_arg = request.args.get('year')
    if year_arg is None:
        filtered = df
    else:
        try:
            year = int(year_arg)
            filtered = df[df['Draft Year'] == year]
        except ValueError:
            filtered = df
    return jsonify(filtered.to_dict(orient='records'))

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json or {}
    pos  = data.pop('Position Group', None)
    model = models.get(pos)
    if model is None:
        return jsonify({'error': f"No model for {pos}"}), 400

    # ─── Raw inputs ─────────────────────────────────────────────
    age        = float(data['Age'])
    height_in  = float(data['Height'])       # inches
    weight_lbs = float(data['Weight'])       # lbs
    ct_win     = float(data['CT_Win%'])
    ct_sos     = float(data['CT_SOS'])
    gs_pct     = float(data['C_GS%'])
    mpg        = float(data['C_MPG'])
    usg_pct    = float(data['C_USG%'])
    fg_pct     = float(data['C_FG%'])
    fga        = float(data['FGA_per_game'])
    threep_pct = float(data['C_3P%'])
    threepa    = float(data['3PA_per_game'])
    ft_pct     = float(data['C_FT%'])
    fta        = float(data['FTA_per_game'])
    ast_raw    = float(data['AST_per_game'])
    stl_raw    = float(data['STL_per_game'])
    tov_raw    = float(data['TOV_per_game'])
    ppg        = float(data['PPG'])
    off_reb    = float(data['OffReb'])
    def_reb    = float(data['DefReb'])
    blk_raw    = float(data.get('BLK_per_game', 0))

    obpm   = float(data.get('C_OBPM', 0))
    dbpm   = float(data.get('C_DBPM', 0))
    bpm    = float(data.get('C_BPM', 0))
    ows    = float(data.get('C_OWS', 0))
    dws    = float(data.get('C_DWS', 0))
    ws     = float(data.get('C_WS', 0))
    ast_pct= float(data.get('C_AST%', 0))
    tov_pct= float(data.get('C_TOV%', 0))
    blk_pct= float(data.get('C_BLK%', 0))
    trb_pct= float(data.get('C_TRB%', 0))

    # ─── Derivations ────────────────────────────────────────────
    height_cm = height_in * 2.54
    bmi       = (weight_lbs * 0.45359237) / ((height_cm/100)**2)

    ts_denom = fga + 0.44 * fta
    ts_pct   = (ppg / (2 * ts_denom) * 100) if ts_denom else 0

    ast_to   = ast_raw / tov_raw if tov_raw else 0
    orb_drb  = off_reb / def_reb if def_reb else 0
    total_reb = off_reb + def_reb

    def per40(x): return (x / mpg * 40) if mpg else 0
    fga_40     = per40(fga)
    threepa_40 = per40(threepa)
    fta_40     = per40(fta)
    ast_40     = per40(ast_raw)
    stl_40     = per40(stl_raw)
    tov_40     = per40(tov_raw)
    pts_40     = per40(ppg)
    trb_40     = per40(total_reb)
    blk_40     = per40(blk_raw)

    # ─── Feature vectors ────────────────────────────────────────
    if pos == 'Guards':
        features = [
            age, height_cm, bmi,
            ct_win, ct_sos,
            gs_pct, mpg, fg_pct, threep_pct, ft_pct, ts_pct,
            ast_to, orb_drb,
            ast_pct, tov_pct, usg_pct,
            obpm, ows,
            fga_40, threepa_40, fta_40,
            ast_40, stl_40, tov_40, pts_40
        ]
    elif pos == 'Wings':
        features = [
            age, height_cm, bmi,
            ct_win, ct_sos,
            gs_pct, mpg, ts_pct,
            ast_to, orb_drb,
            trb_pct, usg_pct,
            bpm, ws,
            fga_40, threepa_40, fta_40, trb_40,
            ast_40, tov_40, pts_40
        ]
    else:  # Bigs
        features = [
            age, height_cm, bmi,
            ct_win, ct_sos,
            gs_pct, mpg, fg_pct, ft_pct, ts_pct,
            ast_to, orb_drb,
            blk_pct, trb_pct, usg_pct,
            dbpm, dws,
            fga_40, fta_40, trb_40,
            stl_40, blk_40, pts_40
        ]

    score = model.predict([features])[0]
    return jsonify({'Predicted Score': float(score)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
