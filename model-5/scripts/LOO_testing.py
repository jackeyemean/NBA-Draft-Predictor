import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict

# config
MIN_YEAR      = 2011
MAX_YEAR      = 2021
TRAIN_PATH    = "model-5/data/TRAINING.csv"
TOP_K         = 50

TRAIN_POSITIONS = ["C"]

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
    "C_AST%", "C_STL%", "C_BLK%", "C_USG%",
    "C_ORtg", "C_DRtg",
    "C_OBPM", "C_DBPM", "C_BPM",

    # ─── College Per-40 Stats ───
    "C_FGA/40", "C_3PA/40", "C_FTA/40",
    "C_TRB/40", "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PTS/40"
]

# Load and filter data
df = pd.read_csv(TRAIN_PATH)
df = df[df["Draft Year"].between(MIN_YEAR, MAX_YEAR)].copy()
#df = df[df["POS"].apply(lambda x: any(p in [i.strip() for i in x.split(",")] for p in TRAIN_POSITIONS))].copy()

def is_big(pos_string: str) -> bool:
    positions = [p.strip() for p in pos_string.split(",")]
    return (
        "C" in positions or
        (positions == ["PF"]) or
        (positions == ["C", "PF"]) or
        (positions == ["PF", "C"])
    )

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
