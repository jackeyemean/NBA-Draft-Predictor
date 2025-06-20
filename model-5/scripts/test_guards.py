import pandas as pd
import joblib
import re

# config
TEST_YEARS   = [2022, 2023, 2024]
MODEL_PATH   = "model-5/guards.pkl"       # your guard‐only model
RAW_DATA_PATH = "model-5/data/TESTING.csv"

# ─── Guard‐only predicate ────────────────────────────────────────────────
GUARD_POS = {"PG", "SG"}

def is_guard_only(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    return all(p in GUARD_POS for p in parts)

# ─── Load data ───────────────────────────────────────────────────────────
df_all = pd.read_csv(RAW_DATA_PATH)
if "Draft Year" not in df_all.columns:
    raise KeyError("Column 'Draft Year' not found in raw data.")
if "POS" not in df_all.columns:
    raise KeyError("Column 'POS' not found in raw data.")

# ─── Filter by draft year ────────────────────────────────────────────────
df_test = df_all[df_all["Draft Year"].isin(TEST_YEARS)].copy()
if df_test.empty:
    raise ValueError(f"No data for Draft Years = {TEST_YEARS}.")

# ─── Keep only pure guards ───────────────────────────────────────────────
df_test = df_test[df_test["POS"].apply(is_guard_only)].copy()
if df_test.empty:
    raise ValueError(f"No guards (PG/SG) in Draft Years {TEST_YEARS}.")

# ─── Load model ─────────────────────────────────────────────────────────
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not find model file at {MODEL_PATH}")

# ─── Features ──────────────────────────────────────────────────────────
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

missing_cols = [c for c in FEATURES if c not in df_test.columns]
if missing_cols:
    raise KeyError(f"Missing required columns in test data: {missing_cols}")

X_test = df_test[FEATURES]

# ─── Predict & rank ─────────────────────────────────────────────────────
predictions = model.predict(X_test)
df_test = df_test.reset_index(drop=True)
df_test["Predicted NBA Career Score"] = predictions

df_ranked = df_test.sort_values(
    by="Predicted NBA Career Score", ascending=False
).reset_index(drop=True)

# ─── Output ─────────────────────────────────────────────────────────────
print(f"\n=== Predicted NBA Career Scores (Guards Only) ===\n")
for idx, row in df_ranked.iterrows():
    name  = row.get("Name", "Unknown")
    year  = row["Draft Year"]
    pos   = row["POS"]
    score = row["Predicted NBA Career Score"]
    print(f"{idx+1:2d}. {name:25} | Year: {year} | POS: {pos:5} | Score: {score:.2f}")
