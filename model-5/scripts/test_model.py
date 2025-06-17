import pandas as pd
import joblib

# config
TEST_POSITIONS = ["SG", "PG"]
TEST_YEARS = [2024]
MODEL_PATH = "model-5/guards.pkl"
RAW_DATA_PATH = "model-5/data/TESTING.csv"

# load data
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

# load model
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    raise FileNotFoundError(f"Could not find model file at {MODEL_PATH}")

FEATURES = [
    # ─── Player Info  ───
    "Age", "Height", "Weight", "BMI",
    "Relatives",

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
    "CT_SRS",
    "CT_ORtg", "CT_DRtg",

    # ─── College Per Game Stats ───
    "C_G", "C_GS%", "C_MPG",
    "C_3P%", "C_FG%", "C_FT%",

    # ─── Feature Engineered ───
    "C_AST_TO", "C_ORB_DRB", "C_BLK_MPG",

    # ─── College Advanced Stats ───
    "C_PER",
    "C_AST%", "C_STL%", "C_BLK%", "C_TRB%", "C_USG%",
    "C_ORtg", "C_DRtg",    
    "C_OBPM", "C_DBPM", "C_BPM", "C_WS/40",

    # ─── College Per-40 Stats ───
    "C_FGA/40", "C_3PA/40", "C_FTA/40",
    "C_TRB/40", "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PTS/40"

    # ─── ARCHIVED ───
    # # Raw NBA team stats (redundant with relative versions)
    # "NBA Win%", "NBA Pace", "NBA PPG", "NBA OPPG", "NBA ORtg", "NBA DRtg",
    # "Rel PPG", "Rel OPPG", "NBA Net PPG", "NBA NRtg"

    # # College team stats (covered by SRS/ORtg/DRtg)
    # "CT_PTS/G", "CT_PTSA/G", "CT_SOS"

    # # College basic box score stats
    # "C_FG", "C_FGA", "C_3P", "C_3PA",
    # "C_FT", "C_FTA", "C_DRB", "C_ORB", "C_TRB", "C_AST", "C_STL", "C_BLK",
    # "C_TOV", "C_PF", "C_PTS"

    # # Additional advanced stats (often redundant or noisy)
    # "C_TS%", "C_3PAr", "C_FTr", "C_PProd",
    # "C_ORB%", "C_DRB%", 
    # "C_OWS", "C_DWS", "C_WS",  "C_TOV%"

    # # Per-40 stats (less predictive / duplicated elsewhere)
    # "C_FG/40", "C_3P/40", "C_FT/40", "C_ORB/40", "C_DRB/40", "C_PF/40"

    # # Per-100 stats (fully excluded)
    # "C_FG/100", "C_FGA/100", "C_3P/100", "C_3PA/100", "C_FT/100", "C_FTA/100",
    # "C_ORB/100", "C_DRB/100", "C_TRB/100", "C_AST/100", "C_STL/100", "C_BLK/100",
    # "C_TOV/100", "C_PF/100", "C_PTS/100"
]

# verify columns exist
missing_cols = [col for col in FEATURES if col not in df_test.columns]
if missing_cols:
    raise KeyError(f"Missing required columns in test data: {missing_cols}")

# prepare feature matrix for prediction
X_test = df_test[FEATURES]

# run predictions
predictions = model.predict(X_test)
df_test = df_test.reset_index(drop=True)
df_test["Predicted NBA Career Score"] = predictions

# sort all players by descending predicted score
df_ranked = df_test.sort_values(
    by="Predicted NBA Career Score", ascending=False
).reset_index(drop=True)

# print results
print(f"\n=== Predicted NBA Career Scores ===\n")
for idx, row in df_ranked.iterrows():
    name = row.get("Name", "Unknown")
    year = row["Draft Year"]
    pos = row["POS"]
    score = row["Predicted NBA Career Score"]
    print(f"{idx+1:2d}. {name:25} | Year: {year} | POS: {pos:5} | Predicted Score: {score:.2f}")
