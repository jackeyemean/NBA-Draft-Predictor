import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv("model-3/data/2011-to-2020-labelled.csv")

IGNORE_YEARS = [2021, 2022, 2023, 2024]
if "Draft Year" in df.columns:
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

FEATURES = [
    "Pick Number", "Age",
    "Height", "Weight", "Height/Weight", "NBA Relatives", "Seasons Played (College)",
    "G", "GS%", "MPG", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
    "FT", "FTA", "FT%", "DRB", "ORB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS",
    "PER", "TS%", "3PAr", "FTr", "PProd",
    "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%",
    "OWS", "DWS", "WS", "WS/40", "OBPM", "DBPM", "BPM",
    "FG/40", "FGA/40", "3P/40", "3PA/40", "FT/40", "FTA/40",
    "ORB/40", "DRB/40", "TRB/40", "AST/40", "STL/40", "BLK/40", "TOV/40", "PF/40", "PTS/40",
    "FG/100", "FGA/100", "3P/100", "3PA/100", "FT/100", "FTA/100",
    "ORB/100", "DRB/100", "TRB/100", "AST/100", "STL/100", "BLK/100", "TOV/100", "PF/100", "PTS/100",
    "ORtg", "DRtg",
    "College Strength"
]
missing_cols = [col for col in FEATURES if col not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns: {missing_cols}")

# target
y = df["NBA Career Score"]

# feature matrix
X = df[FEATURES]

# train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# save model
joblib.dump(model, "model-3/model-3.pkl")
