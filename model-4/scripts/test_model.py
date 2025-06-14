import pandas as pd
import joblib

# ── CONFIG ─────────────────────────────────────────────────────────────────────
TEST_POSITIONS = ["PG", "SG", "SF", "PF", "C"]
TEST_YEARS     = [2024]
MODEL_PATH     = "model-4/all-pos-no-draft-context.pkl"
RAW_DATA_PATH  = "model-4/data/featured-testing.csv"
TRAIN_PATH     = "model-4/data/final-training.csv"
TOP_K          = 74  # num of top correlated features to display

# ── LOAD AND FILTER TEST DATA ─────────────────────────────────────────────────
df_all = pd.read_csv(RAW_DATA_PATH)
if "Draft Year" not in df_all.columns:
    raise KeyError("Column 'Draft Year' not found in raw data.")
if "POS" not in df_all.columns:
    raise KeyError("Column 'POS' not found in raw data.")

# filter by draft year
df_test = df_all[df_all["Draft Year"].isin(TEST_YEARS)].copy()
if df_test.empty:
    raise ValueError(f"No data for Draft Years = {TEST_YEARS}.")

# filter by position
def keep_position(pos_string):
    player_positions = [p.strip() for p in pos_string.split(",")]
    return any(p in player_positions for p in TEST_POSITIONS)

df_test = df_test[df_test["POS"].apply(keep_position)].copy()
if df_test.empty:
    raise ValueError(f"No rows for positions {TEST_POSITIONS} in Draft Years {TEST_YEARS}.")

# ── DEFINE FEATURES ─────────────────────────────────────────────────────────────
FEATURES = [
    # pick, NBA team, measurements 
    "Age", "Height", "Weight", "BMI",
    # "Relatives",
    #"Pick Number", 
    "Main_POS_C", "Main_POS_PF", "Main_POS_PG", "Main_POS_SF", "Main_POS_SG",

    # primary team's (first 4 seasons) season prior to getting drafted
    #"NBA Dev Score", "NBA Win%", "Rel PPG", "Rel OPPG",
    #"NBA SRS", "Rel ORtg", "Rel DRtg", "NBA Net PPG", "NBA Expected Win%",     
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

# verify test columns
missing_cols = [col for col in FEATURES if col not in df_test.columns]
if missing_cols:
    raise KeyError(f"Missing required columns in test data: {missing_cols}")

# ── PREDICTIONS ────────────────────────────────────────────────────────────────
X_test = df_test[FEATURES]
model = joblib.load(MODEL_PATH)
predictions = model.predict(X_test)

df_test = df_test.reset_index(drop=True)
df_test["Predicted Player Tier"] = predictions

# print predicted ranking
df_ranked = df_test.sort_values(by="Predicted Player Tier", ascending=False).reset_index(drop=True)
print("\n=== Predicted Player Tiers ===\n")
for idx, row in df_ranked.iterrows():
    name  = row.get("Name", "Unknown")
    year  = row["Draft Year"]
    pos   = row["POS"]
    score = row["Predicted Player Tier"]
    print(f"{idx+1:2d}. {name:25} | Year: {year} | POS: {pos:5} | Predicted Score: {score:.2f}")

# ── CORRELATION ANALYSIS ────────────────────────────────────────────────────────
df_train = pd.read_csv(TRAIN_PATH)
# ensure all features present
missing_train = [col for col in FEATURES + ["Player Tier"] if col not in df_train.columns]
if missing_train:
    raise KeyError(f"Missing columns in training set: {missing_train}")

corrs = df_train[FEATURES + ["Player Tier"]].corr()["Player Tier"].abs().drop("Player Tier").sort_values(ascending=False)
print(f"\nTop {TOP_K} features by |corr| with Player Tier:\n")
for feat, corr_val in corrs.head(TOP_K).items():
    print(f"{feat:20s}: {corr_val:.3f}")
