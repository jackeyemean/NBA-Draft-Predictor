from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
from models import models

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

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
    payload = request.json or {}
    code = payload.pop('Position Group', None)
    model = models.get(code)
    if model is None:
        return jsonify({'error': f"No model for {code}"}), 400

    # Build feature list: for Wings, duplicate C_TS%
    if code == 'Wings':
        try:
            features = [
                payload['Age'], payload['Height'], payload['BMI'],
                payload['CT_Win%'], payload['CT_SOS'],
                payload['C_GS%'], payload['C_MPG'],
                # duplicate C_TS% here:
                payload['C_TS%'], payload['C_TS%'],
                payload['C_AST_TO'], payload['C_ORB_DRB'],
                payload['C_TRB%'], payload['C_USG%'],
                payload['C_BPM'], payload['C_WS'],
                payload['C_FGA/40'], payload['C_3PA/40'], payload['C_FTA/40'],
                payload['C_TRB/40'], payload['C_AST/40'], payload['C_TOV/40'],
                payload['C_PTS/40']
            ]
        except KeyError as e:
            return jsonify({'error': f"Missing feature {e.args[0]}"}), 400
    else:
        # Guards & Bigs use a single value per feature
        # Assuming payload only contains exactly the right keys in order:
        features = list(payload.values())

    # Now predict
    score = model.predict([features])[0]
    return jsonify({'Predicted Score': float(score)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
