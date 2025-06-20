import pandas as pd
import re
import joblib
from sklearn.ensemble import RandomForestRegressor

# Config
IGNORE_YEARS    = []
TRAINING_PATH   = "model-5/data/TRAINING.csv"
OUTPUT_PATH     = "model-5/wings.pkl"

# ─── Wing‐only predicate ───────────────────────────────────────────────────────
def is_wing(pos_str: str) -> bool:
    # split on commas, slashes, dashes, or spaces
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    # reject any center
    if "C" in parts:
        return False
    # any SF makes them a wing
    if "SF" in parts:
        return True
    # PF only counts if paired with another non-center position
    if "PF" in parts and len(parts) > 1:
        return True
    return False

# ─── Load & filter ─────────────────────────────────────────────────────────────
df = pd.read_csv(TRAINING_PATH)

# drop ignored years
if "Draft Year" in df.columns and IGNORE_YEARS:
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

# keep only wings
df = df[df["POS"].apply(is_wing)].copy()
if df.empty:
    raise ValueError("No data remains after filtering for wings (SF or multi-role PF).")

# ─── Features & target ─────────────────────────────────────────────────────────
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

missing = [c for c in FEATURES if c not in df.columns]
if missing:
    raise KeyError(f"Missing required columns after wing‐filter: {missing}")

y = df["Player Tier"]
X = df[FEATURES]

# ─── Train & save ─────────────────────────────────────────────────────────────
model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)
model.fit(X, y)

joblib.dump(model, OUTPUT_PATH)
print(f"Wing‐only model saved to {OUTPUT_PATH}")
