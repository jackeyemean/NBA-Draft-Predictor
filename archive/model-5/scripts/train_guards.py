import pandas as pd
import re
import joblib
from sklearn.ensemble import RandomForestRegressor

# Config
MIN_YEAR       = 2011
MAX_YEAR       = 2021
IGNORE_YEARS   = []
TRAIN_PATH     = "model-5/data/TRAINING.csv"
OUTPUT_PATH    = "model-5/guards.pkl"

# ─── Guard‐only predicate ──────────────────────────────────────────────────────
GUARD_POS = {"PG", "SG"}

def is_guard_only(pos_str: str) -> bool:
    # split on commas, slashes, dashes, or spaces
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]  # drop empties
    # every part must be PG or SG
    return all(p in GUARD_POS for p in parts)

# ─── Load & filter ─────────────────────────────────────────────────────────────
df = pd.read_csv(TRAIN_PATH)

# drop ignored years
if "Draft Year" in df.columns and IGNORE_YEARS:
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

# optional year‐range filter
if MIN_YEAR is not None and MAX_YEAR is not None and "Draft Year" in df.columns:
    df = df[df["Draft Year"].between(MIN_YEAR, MAX_YEAR)].copy()

# keep only guards
df = df[df["POS"].apply(is_guard_only)].copy()
if df.empty:
    raise ValueError("No data remains after filtering for guards.")

# ─── Features & target ────────────────────────────────────────────────────────
FEATURES = [
    # Player Info
    "Age", "Height", "Weight", "BMI",
    # College Team Context
    "College Strength", "Seasons Played (College)",
    "CT_Win%", "CT_SRS", "CT_SOS", "CT_ORtg", "CT_DRtg",
    # College Per Game Stats
    "C_G", "C_GS%", "C_MPG",
    # Feature Engineered
    "C_AST_TO",
    # College Advanced Stats
    "C_PER", "C_TS%", "C_AST%", "C_STL%", "C_TRB%", "C_USG%", "C_TOV%",
    "C_OWS", "C_DWS", "C_ORtg", "C_DRtg", "C_WS/40", "C_OBPM", "C_DBPM", "C_BPM",
    # College Per-40 Stats
    "C_FGA/40", "C_3PA/40", "C_FTA/40", "C_TRB/40",
    "C_AST/40", "C_STL/40", "C_TOV/40", "C_PTS/40"
]

# sanity check
missing = [c for c in FEATURES if c not in df.columns]
if missing:
    raise KeyError(f"Missing required columns after guard‐filter: {missing}")

y = df["Player Tier"]
X = df[FEATURES]

# ─── Train & save ─────────────────────────────────────────────────────────────
model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)
model.fit(X, y)

joblib.dump(model, OUTPUT_PATH)
print(f"Guard‐only model saved to {OUTPUT_PATH}")
