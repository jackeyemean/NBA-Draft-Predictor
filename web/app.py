from flask import Flask, render_template, request
import pandas as pd
import os  # path operations

app = Flask(__name__)
# Load predictions CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'all_predictions.csv')
df = pd.read_csv(DATA_PATH)

# Helper to get unique sorted values
def unique_sorted(col):
    return sorted(df[col].dropna().unique())

@app.route('/', methods=['GET'])
def index():
    # Get filter parameters
    year = request.args.get('year')
    position = request.args.get('position')

    # Apply filters
    filtered = df
    if year:
        filtered = filtered[filtered['Draft Year'] == int(year)]
    if position:
        filtered = filtered[filtered['Position Group'] == position]

    # Sort by predicted score descending
    filtered = filtered.sort_values(by='Predicted Score', ascending=False)

    # Prepare template data
    players = filtered.to_dict(orient='records')
    years = unique_sorted('Draft Year')
    positions = unique_sorted('Position Group')

    return render_template('index.html', years=years, positions=positions, players=players)

if __name__ == '__main__':
    app.run(debug=True)