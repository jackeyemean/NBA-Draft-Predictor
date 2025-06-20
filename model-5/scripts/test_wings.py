import pandas as pd
import joblib
import re

# config
TEST_YEARS    = [2022, 2023, 2024]
MODEL_PATH    = "model-5/wings.pkl"       # your wing‐only model
RAW_DATA_PATH = "model-5/data/TESTING.csv"

# ─── Wing‐only predicate ───────────────────────────────────────────────────────
def is_wing(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    if "C" in parts:
        return False
    if "SF" in parts:
        return True
    if "PF" in parts and len(parts) > 1:
        return True
    return False

# ─── Load & checks ───────────────────────────────────────────────────────────
df_all = pd.read_csv(RAW_DATA_PATH)
if "Draft Year" not in df_all.columns or "POS" not in df_all.columns:
    raise KeyError("Required columns 'Draft Year' or 'POS' missing in raw data.")

# ─── Filter by draft year ────────────────────────────────────────────────────
df_test = df_all[df_all["Draft Year"].isin(TEST_YEARS)].copy()
if df_test.empty:
    raise ValueError(f"No data for Draft Years = {TEST_YEARS}.")

# ─── Keep only wings ─────────────────────────────────────────────────────────
df_test = df_test[df_test["POS"].apply(is_wing)].copy()
if df_test.empty:
    raise ValueError(f"No wings (SF or multi-role PF) in Draft Years {TEST_YEARS}.")

# ─── Load model ─────────────────────────────────────────────────────────────
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not find model file at {MODEL_PATH}")

# ─── Features ───────────────────────────────────────────────────────────────
FEATURES = [
    # ─── Player Info  ───
    "Age", "Height", "Weight", "BMI", 
    #"Relatives",

    # ─── Post Draft Context ───
    #"Pick Number",    
    #"NBA Dev Score",
    #"NBA Expected Win%",
    #"NBA SRS",
    #"Rel ORtg", "Rel DRtg", "Rel NBA Pace",

    # ─── College Team Context ───
    "College Strength",
    "Seasons Played (College)",
    "CT_Win%",
    "CT_SRS", "CT_SOS",
    "CT_ORtg", "CT_DRtg",

    # ─── College Per Game Stats ───
    "C_G", "C_GS%", "C_MPG",
    #"C_3P%", "C_FG%", "C_FT%",

    # ─── Feature Engineered ───
    "C_AST_TO", "C_ORB_DRB", "C_BLK_MPG",

    # ─── College Advanced Stats ───
    "C_PER",
    "C_TS%",
    "C_AST%", "C_STL%", "C_BLK%", "C_TRB%", "C_USG%",  "C_TOV%",
    "C_OWS", "C_DWS", #"C_WS",
    "C_ORtg", "C_DRtg", "C_WS/40",
    "C_OBPM", "C_DBPM", "C_BPM",

    # ─── College Per-40 Stats ───
    "C_FGA/40", "C_3PA/40", "C_FTA/40",
    "C_TRB/40", "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PTS/40"

    # ─── ARCHIVED ───
    # # Raw NBA team stats (redundant with relative versions)
    # "NBA Win%", "NBA Pace", "NBA PPG", "NBA OPPG", "NBA ORtg", "NBA DRtg",
    # "Rel PPG", "Rel OPPG", "NBA Net PPG", "NBA NRtg"

    # # College team stats (covered by SRS/ORtg/DRtg)
    # "CT_PTS/G", "CT_PTSA/G",

    # # College basic box score stats
    # "C_FG", "C_FGA", "C_3P", "C_3PA",
    # "C_FT", "C_FTA", "C_DRB", "C_ORB", "C_TRB", "C_AST", "C_STL", "C_BLK",
    # "C_TOV", "C_PF", "C_PTS"

    # # Additional advanced stats (often redundant or noisy)
    # "C_3PAr", "C_FTr", "C_PProd",
    # "C_ORB%", "C_DRB%",
    # 

    # # Per-40 stats (less predictive / duplicated elsewhere)
    # "C_FG/40", "C_3P/40", "C_FT/40", "C_ORB/40", "C_DRB/40", "C_PF/40"

    # # Per-100 stats (fully excluded)
    # "C_FG/100", "C_FGA/100", "C_3P/100", "C_3PA/100", "C_FT/100", "C_FTA/100",
    # "C_ORB/100", "C_DRB/100", "C_TRB/100", "C_AST/100", "C_STL/100", "C_BLK/100",
    # "C_TOV/100", "C_PF/100", "C_PTS/100"
]

missing = [c for c in FEATURES if c not in df_test.columns]
if missing:
    raise KeyError(f"Missing required columns in test data: {missing}")

# ─── Predict & rank ─────────────────────────────────────────────────────────
X_test = df_test[FEATURES]
predictions = model.predict(X_test)

df_test = df_test.reset_index(drop=True)
df_test["Predicted NBA Career Score"] = predictions

df_ranked = df_test.sort_values(
    by="Predicted NBA Career Score", ascending=False
).reset_index(drop=True)

# ─── Output ────────────────────────────────────────────────────────────────
print(f"\n=== Predicted NBA Career Scores (Wings Only) ===\n")
for idx, row in df_ranked.iterrows():
    name  = row.get("Name", "Unknown")
    year  = row["Draft Year"]
    pos   = row["POS"]
    score = row["Predicted NBA Career Score"]
    print(f"{idx+1:2d}. {name:25} | Year: {year} | POS: {pos:5} | Score: {score:.2f}")
