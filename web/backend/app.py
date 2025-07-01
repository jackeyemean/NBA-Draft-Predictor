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
    features = list(payload.values())

    # Now predict
    score = model.predict([features])[0]
    return jsonify({'Predicted Score': float(score)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
