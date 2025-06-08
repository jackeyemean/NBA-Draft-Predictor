import os
import pandas as pd

# ─────── show full output ───────
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 0)
pd.set_option('display.max_colwidth', None)

RAW_DATA_PATH = "raw-data/drafts-2008-to-2024.csv"
OUT_DIR = "model-3/data"

# For future: 
# college win %, college success, drafted team win %, team dev score

# list of columns to keep from raw data CSVs
KEEP_COLUMNS = [
    "Pick Number", "Age", "College",
    "Height", "Weight", "Height/Weight", "NBA Relatives", "Seasons Played (College)",
    "G", "GS%", "MPG", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
    "FT", "FTA", "FT%", "DRB", "ORB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS",
    "PER", "TS%", "3PAr", "FTr", "PProd",
    "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%",
    "OWS", "DWS", "WS", "WS/40", "OBPM", "DBPM", "BPM",
    "FG/40", "FGA/40", "3P/40", "3PA/40", "FT/40", "FTA/40",
    "ORB/40", "DRB/40", "TRB/40", "AST/40", "STL/40", "BLK/40", "TOV/40", "PF/40", "PTS/40",
    "FG/100", "FGA/100", "3P/100", "3PA/100", "FT/100", "FTA/100",
    "ORB/100", "DRB/100", "TRB/100", "AST/100", "STL/100", "BLK/100", "TOV/100", "PF/100", "PTS/100",
    "ORtg", "DRtg",
    "College Strength"
]

COLLEGE_STRENGTH = {
    # Tier 2: Elite blue-bloods
    "Duke":          2,
    "Kentucky":      2,
    "Kansas":        2,
    "UNC":           2,
    "UCLA":          2,

    # Tier 1: Modern power programs
    "Arizona":       1,
    "UConn":         1,
    "Villanova":     1,
    "Florida State": 1,
    "Texas":         1,
    "Michigan State":1,
    "Louisville":    1,
    "Michigan":      1,
    "Indiana":       1,
    "Gonzaga":       1,
    "USC":           1,
    "Virginia":      1,
    "Oklahoma":      1,
    "Ohio State":    1,
    "Georgia":       1,
    "Colorado":      1,
    "Florida":       1,
    "Baylor":        1,
    "Tennessee":     1,
    "Wisconsin":     1,
    "Purdue":        1,
}

def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def load_data():
    return pd.read_csv(RAW_DATA_PATH)

def engineer_features(df):
    # map college strength
    df["College Strength"] = (
        df["College"]
        .map(COLLEGE_STRENGTH)
        .fillna(0)
        .astype(int)
    )

    return df

def split_and_save(df):
    df_2011_2020 = df[df["Draft Year"].between(2011, 2020)]
    df_2021_2024 = df[df["Draft Year"].between(2021, 2024)]

    path1 = os.path.join(OUT_DIR, "drafts-2011-to-2020-features.csv")
    path2 = os.path.join(OUT_DIR, "drafts-2021-to-2024-features.csv")

    df_2011_2020[KEEP_COLUMNS].to_csv(path1, index=False)
    df_2021_2024[KEEP_COLUMNS].to_csv(path2, index=False)

    print(f"Saved {len(df_2011_2020)} rows to {path1}")
    print(f"Saved {len(df_2021_2024)} rows to {path2}")

def main():
    ensure_out_dir()
    df = load_data()
    df = engineer_features(df)
    split_and_save(df)

if __name__ == "__main__":
    main()
