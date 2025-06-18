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
    # Tier 4: Elite Blue Bloods (Top-tier success + NBA pipelines)
    "Duke": 4,
    "Kentucky": 4,
    "Kansas": 4,
    "UNC": 4,

    # Tier 3: NBA Factories / Near-blue bloods (many recent pros or contending teams)
    "UCLA": 3,
    "Arizona": 3,
    "UConn": 3,
    "Villanova": 3,
    "Gonzaga": 3,
    "Michigan State": 3,
    "Texas": 3,
    "Alabama": 3,
    "Houston": 3,
    "Baylor": 3,

    # Tier 2: Strong Power Programs
    "Florida": 2,
    "Virginia": 2,
    "Tennessee": 2,
    "Arkansas": 2,
    "Oregon": 2,
    "Auburn": 2,
    "Michigan": 2,
    "Indiana": 2,
    "USC": 2,
    "Ohio State": 2,
    "Purdue": 2,
    "Creighton": 2,
    "Marquette": 2,
    "Illinois": 2,
    "Miami (FL)": 2,
    "LSU": 2,
    "Iowa": 2,

    # Tier 1: Solid/NBA-adjacent teams, but not as consistent
    "Florida State": 1,
    "Oklahoma": 1,
    "Georgia": 1,
    "Wisconsin": 1,
    "Colorado": 1,
    "Texas Tech": 1,
    "Seton Hall": 1,
    "Syracuse": 1,
    "Providence": 1,
    "NC State": 1,
    "Maryland": 1,
    "Saint Mary's": 1,
    "Dayton": 1,
    "Memphis": 1,
    "Wake Forest": 1,
    "Missouri": 1,
    "Arizona State": 1,

    # Tier 0: Other (default fallback for anything not listed)
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
