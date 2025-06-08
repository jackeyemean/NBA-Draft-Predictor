import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict

# ── CONFIG ─────────────────────────────────────────────────────────────────────

MIN_YEAR = 2011
MAX_YEAR = 2020

# Positions to keep
TRAIN_POSITIONS = ["C"]

# Path to your CSV file
RAW_DATA_PATH = "model-3/data/2011-to-2020.csv"

# Features to use for training
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

# ── LOAD AND FILTER ──────────────────────────────────────────────────────────────

df = pd.read_csv(RAW_DATA_PATH)

# 1. Keep only years 2008 to 2020 (inclusive)
if "Draft Year" not in df.columns:
    raise KeyError("Column 'Draft Year' not found in the CSV.")
mask_years = df["Draft Year"].between(MIN_YEAR, MAX_YEAR)
df = df[mask_years].copy()
if df.empty:
    raise ValueError(f"No data remains for Draft Years {MIN_YEAR}–{MAX_YEAR}.")

# 2. Keep only rows whose POS contains at least one of TRAIN_POSITIONS
def keep_position(pos_string: str) -> bool:
    player_positions = [p.strip() for p in pos_string.split(",")]
    return any(p in player_positions for p in TRAIN_POSITIONS)

if "POS" not in df.columns:
    raise KeyError("Column 'POS' not found in the CSV.")
df = df[df["POS"].apply(keep_position)].copy()
if df.empty:
    raise ValueError(f"No rows remain after filtering for positions {TRAIN_POSITIONS}.")

# 3. Verify that all FEATURES are present
missing_cols = [col for col in FEATURES if col not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns after filtering: {missing_cols}")

# 4. Verify target column
if "NBA Career Score" not in df.columns:
    raise KeyError("Column 'NBA Career Score' not found in the CSV.")

# ── PREPARE X, y ─────────────────────────────────────────────────────────────────

X = df[FEATURES]
y = df["NBA Career Score"]

# ── LEAVE-ONE-OUT CROSS-PREDICT ───────────────────────────────────────────────────

loo = LeaveOneOut()
model = RandomForestRegressor(n_estimators=100, random_state=42)

# cross_val_predict with LeaveOneOut will, for each row, train on all other rows and predict for that row
predictions = cross_val_predict(
    model,
    X,
    y,
    cv=loo,
    n_jobs=-1,     # use all cores if available; remove or set n_jobs=1 if it causes issues
    verbose=0
)

# ── COMBINE RESULTS ───────────────────────────────────────────────────────────────

# Make a copy so we don’t overwrite the original DataFrame
df_results = df.reset_index(drop=True).copy()
df_results["Predicted NBA Career Score"] = predictions
df_results["Original NBA Career Score"] = df_results["NBA Career Score"]

# Keep only the columns we care about in the final output
# (Name, Draft Year, POS are assumed to exist; adjust if your column names differ)
COLUMNS_TO_KEEP = ["Name", "Draft Year", "POS", "Predicted NBA Career Score", "Original NBA Career Score"]
for col in COLUMNS_TO_KEEP:
    if col not in df_results.columns:
        raise KeyError(f"Column '{col}' not found in the data; please adjust COLUMNS_TO_KEEP.")

df_final = df_results[COLUMNS_TO_KEEP].sort_values(
    by="Predicted NBA Career Score",
    ascending=False
).reset_index(drop=True)

# ── PRINT RESULTS ────────────────────────────────────────────────────────────────

print("\n=== Hold-Out Predictions (2011–2020) ===\n")
print(f"{'Rank':>4} | {'Name':30} | {'Year':>4} | {'POS':>5} | {'Predicted':>10} | {'Original':>8}")
print("-" * 80)
for idx, row in df_final.iterrows():
    rank = idx + 1
    name = row["Name"]
    year = int(row["Draft Year"])
    pos = row["POS"]
    pred_score = row["Predicted NBA Career Score"]
    orig_score = row["Original NBA Career Score"]
    print(f"{rank:4d} | {name:30} | {year:4d} | {pos:5s} | {pred_score:10.2f} | {orig_score:8.2f}")
