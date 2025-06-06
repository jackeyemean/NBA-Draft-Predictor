import pandas as pd
import joblib

# config
TEST_YEARS = [2020]
MODEL_PATH_TEMPLATE = "model-1/holdout-models/holdout-2020.pkl"
RAW_DATA_PATH = "model-1/data/training-data-2011-to-2020.csv"

# load raw data
df_all = pd.read_csv(RAW_DATA_PATH)
if "Draft Year" not in df_all.columns:
    raise KeyError("Column 'Draft Year' not found in raw data.")

# feature columns
FEATURES = [
    "Age", "Height", "Weight", "NBA Relatives", "Seasons Played (College)",
    "G", "GS%", "MPG", "PER", "TS%", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "WS/40", "BPM",
    "FG/100", "FGA/100", "3P/100", "3PA/100", "FT/100", "FTA/100",
    "ORB/100", "DRB/100", "TRB/100", "AST/100", "STL/100", "BLK/100", "TOV/100", "PF/100", "PTS/100",
    "ORtg", "DRtg"
]

for year in TEST_YEARS:
    model_path = MODEL_PATH_TEMPLATE.format(year=year)
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        print(f"Model file not found for year {year}: {model_path}")
        continue

    # only run tests on players drafted in TEST_YEAR
    df_test = df_all[df_all["Draft Year"] == year].copy()
    if df_test.empty:
        print(f"No rows found for Draft Year = {year}. Skipping.")
        continue

    # check for missing feature columns
    missing_cols = [col for col in FEATURES if col not in df_test.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns in test data for year {year}: {missing_cols}")

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

    # print results
    print(f"\n=== Predicted NBA Career Scores for Draft Year {year} ===\n")
    for idx, row in df_ranked.iterrows():
        name = row.get("Name", "Unknown")
        score = row["Predicted NBA Career Score"]
        print(f"{idx+1:2d}. {name:30} | Predicted Score: {score:.2f}")
