import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Config
TRAIN_POSITIONS = ["PG"]
IGNORE_YEARS = []

df = pd.read_csv("model-4/data/training-2011-2021.csv")

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
output_path = f"model-4/pg-no-draft-context.pkl"
joblib.dump(model, output_path)
print(f"Model saved to {output_path}")
