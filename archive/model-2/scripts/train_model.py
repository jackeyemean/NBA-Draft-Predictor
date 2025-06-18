import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# config
TRAIN_POSITIONS = ["PG", "SG", "SF", "PF", "C"]

IGNORE_YEARS = [2020, 2021, 2022, 2023, 2024]

# load data
df = pd.read_csv("model-2/data/labelled-drafts-2008-to-2020.csv")

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
    "Age",
    "Height",
    "Weight",
    "Height/Weight",
    "NBA Relatives",
    "Seasons Played (College)",
    "G",
    "GS%",
    "MPG",
    "FGA",
    "FG%",
    "3PA",
    "3P%",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
    "TS%",
    "TRB%",
    "AST%",
    "BLK%",
    "TOV%",
    "USG%",
    "OWS",
    "DWS"
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
years_omitted_tag = str(IGNORE_YEARS[0])
output_path = f"model-2/holdout-models/holdout-{years_omitted_tag}.pkl"
joblib.dump(model, output_path)
print(f"Model saved to {output_path}")
