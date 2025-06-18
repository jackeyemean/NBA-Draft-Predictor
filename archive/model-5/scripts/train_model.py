import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Config
TRAIN_POSITIONS = ["C"]
IGNORE_YEARS = []

df = pd.read_csv("model-5/data/TRAINING.csv")

# drop ignored years
if "Draft Year" in df.columns and IGNORE_YEARS:
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

# filter by positions
def keep_position(pos_string):
    player_positions = [p.strip() for p in pos_string.split(",")]
    return any(p in player_positions for p in TRAIN_POSITIONS)

df = df[df["POS"].apply(keep_position)].copy()
if df.empty:
    raise ValueError(f"No data remains after filtering for positions {TRAIN_POSITIONS} and ignoring years {IGNORE_YEARS}.")

FEATURES = [
    # ─── Player Info  ───
    "Age", "Height", "Weight", "BMI", "Relatives",

    # ─── Post Draft Context ───
    #"Pick Number",    
    #"NBA Dev Score",
    #"NBA Expected Win%",
    #"NBA SRS",
    #"Rel ORtg", "Rel DRtg", "Rel NBA Pace",

    # ─── College Team Context ───
    "College Strength",
    "Seasons Played (College)",
    #"CT_Win%",
    "CT_SRS", "CT_SOS",
    "CT_ORtg", "CT_DRtg",

    # ─── College Per Game Stats ───
    "C_G", "C_GS%", "C_MPG",
    "C_3P%", "C_FG%", "C_FT%",

    # ─── Feature Engineered ───
    "C_AST_TO", "C_ORB_DRB", "C_BLK_MPG",

    # ─── College Advanced Stats ───
    "C_PER",
    "C_TS%",
    "C_AST%", "C_STL%", "C_BLK%", "C_TRB%", "C_USG%",  "C_TOV%",
    "C_OWS", "C_DWS", "C_WS",
    "C_ORtg", "C_DRtg", #"C_WS/40",
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

# check missing columns
missing_cols = [col for col in FEATURES if col not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns after filtering: {missing_cols}")

# target
y = df["Player Tier"]
X = df[FEATURES]

# train
model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)
model.fit(X, y)

# save
positions_tag = "-".join(TRAIN_POSITIONS)
output_path = f"model-5/C.pkl"
joblib.dump(model, output_path)
print(f"Model saved to {output_path}")
