import os
import pandas as pd

RAW_DATA_PATH = "raw-data/drafts-2008-to-2024.csv"
OUT_DIR = "model-3/data"

TEAM_DESIRABILITY = {
    # Great reputation
    "SAS": 4,
    "GSW": 4,
    "BOS": 4,
    "TOR": 4,
    "MIA": 4,
    "OKC": 4,

    # Good
    "MIL": 3,
    "DEN": 3,
    "MEM": 3,
    "IND": 3,
    "ATL": 3,
    "CLE": 3,
    "ORL": 3,
    "DAL": 3,

    # Average
    "LAC": 2,
    "MIN": 2,
    "LAL": 2,
    "NYK": 2,
    "HOU": 2,

    # Not Ideal
    "BKN": 1,
    "DET": 1,
    "PHI": 1,
    "UTA": 1,
    "POR": 1,

    # Poverty franchises
    "PHX": 0,
    "NOP": 0,
    "SAC": 0,
    "CHI": 0,
    "WAS": 0,
    "CHO": 0,
}

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

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(RAW_DATA_PATH)

    # map draft team abbreviation to desirability score
    df["Team Desirability"] = (
        df["NBA Team"]
        .map(TEAM_DESIRABILITY)
        .fillna(0)
        .astype(int)
    )

    # map college to strength score
    df["College Strength"] = (
        df["College"]
        .map(COLLEGE_STRENGTH)
        .fillna(0)
        .astype(int)
    )

    # split into two eras
    df_2011_2020 = df[df["Draft Year"].between(2011, 2020)]
    df_2021_2024 = df[df["Draft Year"].between(2021, 2024)]

    # save
    df_2011_2020.to_csv(os.path.join(OUT_DIR, "2011-to-2020.csv"), index=False)
    df_2021_2024.to_csv(os.path.join(OUT_DIR, "2021-to-2024.csv"), index=False)

if __name__ == "__main__":
    main()
