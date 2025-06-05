import pandas as pd
import joblib

# config
MODEL_PATH = "models/model_excluding_years.pkl"
TEST_YEAR = 2014
RAW_DATA_PATH = "data/drafts.csv"

model = joblib.load(MODEL_PATH)
df_all = pd.read_csv(RAW_DATA_PATH)

if "Draft Year" not in df_all.columns:
    raise KeyError("Column 'Draft Year' not found in raw data.")

# only run tests on players drafted in TEST_YEAR
df_test = df_all[df_all["Draft Year"] == TEST_YEAR].copy()
if df_test.empty:
    raise ValueError(f"No rows found for Draft Year = {TEST_YEAR}.")


# feature columns
FEATURES = [
    "Age", "Height", "Weight", "NBA Relatives", "Seasons Played (College)",
    "G", "GS%", "MPG", "PER", "TS%", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "WS/40", "BPM",
    "FG/100", "FGA/100", "3P/100", "3PA/100", "FT/100", "FTA/100",
    "ORB/100", "DRB/100", "TRB/100", "AST/100", "STL/100", "BLK/100", "TOV/100", "PF/100", "PTS/100",
    "ORtg", "DRtg"
]
missing_cols = [col for col in FEATURES if col not in df_test.columns]
if missing_cols:
    raise KeyError(f"Missing required columns in test data: {missing_cols}")


# prepare feature matrix for prediction
X_test = df_test[FEATURES]

# run predictions
predictions = model.predict(X_test)

df_test = df_test.reset_index(drop=True)
df_test["Predicted NBA Career Score"] = predictions

# sort to view descending predicted scores 
df_ranked = df_test.sort_values(
    by="Predicted NBA Career Score", ascending=False
).reset_index(drop=True)

# print
print(f"\n=== Predicted NBA Career Scores for Draft Year {TEST_YEAR} ===\n")
for idx, row in df_ranked.iterrows():
    name = row.get("Name", "Unknown")
    score = row["Predicted NBA Career Score"]
    print(f"{idx+1:2d}. {name:30} | Predicted Score: {score:.2f}")

