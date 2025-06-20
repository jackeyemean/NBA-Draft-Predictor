import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict
import re

# config
MIN_YEAR      = 2011
MAX_YEAR      = 2021
TRAIN_PATH    = "model-5/data/TRAINING.csv"
TOP_K         = 50

TRAIN_POSITIONS = ["C"]

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
    #"C_AST_TO", 
    "C_BLK_MPG",
    "C_ORB_DRB",

    # ─── College Advanced Stats ───
    "C_PER",
    "C_TS%",
    "C_AST%", "C_STL%", "C_TRB%", "C_USG%",  "C_TOV%",
    "C_BLK%",
    "C_OWS", "C_DWS", #"C_WS",
    "C_ORtg", "C_DRtg", "C_WS/40",
    "C_OBPM", "C_DBPM", "C_BPM",

    # ─── College Per-40 Stats ───
    "C_FGA/40", "C_3PA/40", "C_FTA/40",
    "C_TRB/40", "C_AST/40", "C_STL/40", "C_TOV/40", "C_PTS/40",
    "C_BLK/40"

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
def is_big(pos_str: str) -> bool:
    # split on commas, slashes, dashes, or spaces
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]  # drop empty
    # true if they ever played C, or if the only position(s) is PF
    return ("C" in parts) or all(p == "PF" for p in parts)

df = pd.read_csv(TRAIN_PATH)
df = df[df["Draft Year"].between(MIN_YEAR, MAX_YEAR)].copy()
df = df[df["POS"].apply(is_big)].copy()

# Checks
missing_cols = [c for c in FEATURES if c not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns: {missing_cols}")
if "Player Tier" not in df.columns:
    raise KeyError("Column 'Player Tier' not found in CSV.")

# Split
X = df[FEATURES]
y = df["Player Tier"]

# LOO Cross-Validation
loo = LeaveOneOut()
model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)
preds = cross_val_predict(model, X, y, cv=loo, n_jobs=-1, verbose=1)

# Output predictions
df_out = df.reset_index(drop=True).copy()
df_out["Predicted Player Tier"] = preds
df_out["Original Player Tier"] = df_out["Player Tier"]

cols = ["Name", "Draft Year", "POS", "Predicted Player Tier", "Original Player Tier"]
df_final = df_out[cols].sort_values(by="Predicted Player Tier", ascending=False).reset_index(drop=True)

# Print grouped by draft year, sorted by predicted tier
print("\n=== Hold-Out Predictions by Draft Year (Grouped & Sorted) ===\n")
years = sorted(df_final["Draft Year"].unique())

for year in years:
    df_year = df_final[df_final["Draft Year"] == year].sort_values(by="Predicted Player Tier", ascending=False).reset_index(drop=True)
    print(f"\n--- Draft Class {year}, No Draft Context ---\n")
    print(f"{'Rank':>4} | {'Name':30} | {'POS':>5} | {'Predicted':>10} | {'Actual':>8}")
    print("-" * 65)
    for i, row in df_year.iterrows():
        print(f"{i+1:4d} | {row['Name']:30} | {row['POS']:5s} | {row['Predicted Player Tier']:10.2f} | {row['Original Player Tier']:8.2f}")

# Correlation-based feature relevance
df_train = pd.read_csv(TRAIN_PATH)
corrs = df_train[FEATURES + ['Player Tier']].corr()['Player Tier']
abs_corrs = corrs.abs().drop('Player Tier').sort_values(ascending=False)

print(f"\nTop {TOP_K} features by |Pearson corr| with Player Tier:\n")
for feat, val in abs_corrs.head(TOP_K).items():
    print(f"{feat:25s}: {val:.3f}")

# Train full model for feature importance
model.fit(X, y)
importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)

print(f"\nTop {TOP_K} features by RandomForest importance:\n")
for feat, val in importances.head(TOP_K).items():
    print(f"{feat:25s}: {val:.3f}")
