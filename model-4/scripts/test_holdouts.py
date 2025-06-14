import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict

# ── CONFIG ─────────────────────────────────────────────────────────────────────
MIN_YEAR     = 2011
MAX_YEAR     = 2021
TRAIN_PATH   = "model-4/data/final-training.csv"
RAW_DATA_PATH= TRAIN_PATH
TOP_K        = 10  # number of top correlated features to display

TRAIN_POSITIONS = ["PG", "SG", "SF", "PF", "C"]

FEATURES = [
    # pick, NBA team, measurements 
    "Age", "Height", "Weight", "BMI",
    # "Relatives",
    "Pick Number", 
    "Main_POS_C", "Main_POS_PF", "Main_POS_PG", "Main_POS_SF", "Main_POS_SG",

    # primary team's (first 4 seasons) season prior to getting drafted
    "NBA Dev Score", "NBA Win%", "Rel PPG", "Rel OPPG",
    "NBA SRS", "Rel ORtg", "Rel DRtg", "NBA Net PPG", "NBA Expected Win%",     
    # "NBA PPG", "NBA OPPG", "NBA ORtg", "NBA DRtg", "NBA NRtg", "NBA Pace",  

    # college team context
    "College Strength", "Seasons Played (College)", "CT_Win%", "CT_PTS/G", "CT_PTSA/G",
    "CT_SRS", "CT_SOS", "CT_ORtg", "CT_DRtg",

    # college per-game stats
    "C_G", "C_GS%", "C_MPG", "C_AST_TO", "C_ORB_DRB", "C_BLK_MPG",	
    # "C_FG", "C_FGA", "C_3P", "C_3PA", 
    #"C_FT", "C_FTA", "C_DRB", "C_ORB", "C_TRB", "C_AST", "C_STL", "C_BLK",
    #"C_TOV", "C_PF", "C_PTS",
    "C_3P%", "C_FG%", "C_FT%",

    # college advanced stats
    "C_PER", "C_TS%", "C_3PAr", "C_FTr", "C_PProd", "C_ORB%", "C_DRB%", "C_TRB%", "C_AST%",
    "C_STL%", "C_BLK%", "C_TOV%", "C_USG%", "C_OWS", "C_DWS", "C_WS", "C_WS/40",
    "C_OBPM", "C_DBPM", "C_BPM",

    # college per-40 stats
    #"C_FG/40", "C_FGA/40", "C_3P/40", "C_3PA/40", "C_FT/40", "C_FTA/40", "C_ORB/40",
    #"C_DRB/40", "C_TRB/40", "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PF/40", "C_PTS/40",

    # college per-100 stats
    "C_FG/100", "C_FGA/100", "C_3P/100", "C_3PA/100", "C_FT/100", "C_FTA/100", "C_ORB/100",
    "C_DRB/100", "C_TRB/100", "C_AST/100", "C_STL/100", "C_BLK/100", "C_TOV/100", "C_PF/100", "C_PTS/100",
    "C_ORtg", "C_DRtg"
]

# ── LOAD AND FILTER ──────────────────────────────────────────────────────────────
df = pd.read_csv(RAW_DATA_PATH)

# 1. Year filter
if "Draft Year" not in df.columns:
    raise KeyError("Column 'Draft Year' not found in CSV.")
df = df[df["Draft Year"].between(MIN_YEAR, MAX_YEAR)].copy()
if df.empty:
    raise ValueError(f"No data for years {MIN_YEAR}-{MAX_YEAR}.")

# 2. Position filter
def keep_position(pos_string: str) -> bool:
    player_positions = [p.strip() for p in pos_string.split(",")]
    return any(p in player_positions for p in TRAIN_POSITIONS)

if "POS" not in df.columns:
    raise KeyError("Column 'POS' not found in CSV.")
df = df[df["POS"].apply(keep_position)].copy()
if df.empty:
    raise ValueError(f"No rows remain after filtering for positions {TRAIN_POSITIONS}.")

# 3. Feature presence
missing_cols = [c for c in FEATURES if c not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns: {missing_cols}")

# 4. Target presence
if "Player Tier" not in df.columns:
    raise KeyError("Column 'Player Tier' not found in CSV.")

# ── PREPARE DATA ─────────────────────────────────────────────────────────────────
X = df[FEATURES]
y = df["Player Tier"]

# ── LEAVE-ONE-OUT PREDICTIONS ─────────────────────────────────────────────────────
loo = LeaveOneOut()
model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)

preds = cross_val_predict(
    model,
    X, y,
    cv=loo,
    n_jobs=-1,
    verbose=1
)

# ── COMBINE & PRINT ──────────────────────────────────────────────────────────────
df_out = df.reset_index(drop=True).copy()
df_out["Predicted Player Tier"] = preds
df_out["Original Player Tier"] = df_out["Player Tier"]

cols = ["Name","Draft Year","POS","Predicted Player Tier","Original Player Tier"]
for c in cols:
    if c not in df_out.columns:
        raise KeyError(f"Column '{c}' missing; adjust cols list.")

df_final = df_out[cols].sort_values(by="Predicted Player Tier", ascending=False).reset_index(drop=True)

print("\n=== Hold-Out Predictions (2011–2021) ===\n")
print(f"{'Rank':>4} | {'Name':30} | {'Year':>4} | {'POS':>5} | {'Pred':>10} | {'Orig':>8}")
print("-"*80)
for i,row in df_final.iterrows():
    print(f"{i+1:4d} | {row['Name']:30} | {int(row['Draft Year']):4d} | {row['POS']:5s} | {row['Predicted Player Tier']:10.2f} | {row['Original Player Tier']:8.2f}")

# ── CORRELATION ANALYSIS ─────────────────────────────────────────────────────────
df_train = pd.read_csv(TRAIN_PATH)
missing_train = [c for c in FEATURES+['Player Tier'] if c not in df_train.columns]
if missing_train:
    raise KeyError(f"Missing cols in training set: {missing_train}")

corrs = df_train[FEATURES + ['Player Tier']].corr()['Player Tier']
abs_corrs = corrs.abs().drop('Player Tier').sort_values(ascending=False)

print(f"\nTop {TOP_K} features by |corr| with Player Tier:\n")
for feat,val in abs_corrs.head(TOP_K).items():
    print(f"{feat:20s}: {val:.3f}")
