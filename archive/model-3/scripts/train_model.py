import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# config
TRAIN_POSITIONS = ["PG"]

IGNORE_YEARS = []

# load data
df = pd.read_csv("model-3/data/2011-to-2020.csv")

# drop rows from IGNORE_YEARS
if "Draft Year" in df.columns and IGNORE_YEARS: 
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

# keep rows where POS includes at least one of TRAIN_POSITIONS
def keep_position(pos_string):
    player_positions = [p.strip() for p in pos_string.split(",")]
    return any(p in player_positions for p in TRAIN_POSITIONS)

df = df[df["POS"].apply(keep_position)].copy()
if df.empty:
    raise ValueError(f"No data remains after filtering for positions {TRAIN_POSITIONS} and ignoring years {IGNORE_YEARS}.")

# data used
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
    "College Strength", "Team Desirability"
]
missing_cols = [col for col in FEATURES if col not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns after filtering: {missing_cols}")

# target
y = df["NBA Career Score"]
# feature matrix
X = df[FEATURES]

# train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# save model
positions_tag = "-".join(TRAIN_POSITIONS)
output_path = f"model-3/model-3.pkl"
joblib.dump(model, output_path)
print(f"Model saved to {output_path}")
