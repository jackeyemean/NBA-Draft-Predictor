#!/usr/bin/env python3
import sys
import pandas as pd

# -------------------------------------------------------------------
# Feature-importance lists
GUARD_IMPORTANCES = [
    ("Age",         0.241755),
    ("C_OBPM",      0.168257),
    ("C_TS%",       0.059898),
    ("CT_SOS",      0.052836),
    ("BMI",         0.049914),
    ("C_FTA/40",    0.031081),
    ("C_3P%",       0.030527),
    ("C_FG%",       0.030406),
    ("C_STL/40",    0.029063),
    ("C_3PA/40",    0.028527),
    ("C_FT%",       0.026887),
    ("C_PTS/40",    0.025233),
    ("C_OWS",       0.025012),
    ("Height",      0.024215),
    ("CT_Win%",     0.024175),
    ("C_TOV%",      0.022257),
    ("C_MPG",       0.021677),
    ("C_AST_TO",    0.020444),
    ("C_TOV/40",    0.018932),
    ("C_AST%",      0.016323),
    ("C_FGA/40",    0.015238),
    ("C_USG%",      0.013121),
    ("C_GS%",       0.012512),
    ("C_AST/40",    0.011710),
]

WING_IMPORTANCES = [
    ("Age",       0.212667),
    ("C_BPM",     0.070827),
    ("CT_Win%",   0.056256),
    ("C_TRB%",    0.052520),
    ("C_AST/40",  0.051275),
    ("C_USG%",    0.050606),
    ("C_WS",      0.049271),
    ("C_TRB/40",  0.040971),
    ("C_AST_TO",  0.039701),
    ("CT_SOS",    0.038283),
    ("Height",    0.035691),
    ("C_FTA/40",  0.035306),
    ("C_MPG",     0.035230),
    ("C_PTS/40",  0.032996),
    ("C_ORB_DRB", 0.032738),
    ("BMI",       0.031839),
    ("C_TOV/40",  0.030297),
    ("C_FGA/40",  0.026132),
    ("C_3PA/40",  0.025455),
    ("C_TS%",     0.018134),
    ("C_TS%",     0.017296),
    ("C_GS%",     0.016509),
]

BIG_IMPORTANCES = [
    ("Age",       0.192663),
    ("C_DBPM",    0.112351),
    ("C_DWS",     0.104068),
    ("C_MPG",     0.084462),
    ("C_STL/40",  0.054049),
    ("C_TS%",     0.046877),
    ("C_FT%",     0.044851),
    ("CT_Win%",   0.042257),
    ("C_TRB/40",  0.035267),
    ("BMI",       0.035214),
    ("CT_SOS",    0.029486),
    ("C_FG%",     0.025728),
    ("C_TRB%",    0.025037),
    ("C_FTA/40",  0.023004),
    ("C_FGA/40",  0.020969),
    ("C_USG%",    0.020690),
    ("C_BLK%",    0.019925),
    ("C_ORB_DRB", 0.018537),
    ("C_GS%",     0.018459),
    ("C_BLK/40",  0.017331),
    ("C_PTS/40",  0.016575),
    ("Height",    0.012201),
]

def print_importances(title, imps):
    print(f"\nFeature importances for {title}:")
    for feat, imp in imps:
        print(f"{feat.ljust(12)} | {imp:.6f}")

def print_group(name, df):
    cols = ["Name", "Draft Year", "Predicted Score", "Actual Tier"]
    # compute max width for each column
    widths = {}
    for col in cols:
        max_cell = df[col].astype(str).map(len).max() if not df.empty else 0
        widths[col] = max(len(col), max_cell)
    # header
    print(f"\n=== {name} ===")
    header = " | ".join(f"{col:<{widths[col]}}" for col in cols)
    print(header)
    # separator row
    sep = "-+-".join("-" * widths[col] for col in cols)
    print(sep)
    # data rows
    for _, row in df.iterrows():
        row_str = " | ".join(f"{str(row[col]):<{widths[col]}}" for col in cols)
        print(row_str)

def main(path):
    df = pd.read_csv(path)
    df = df.sort_values("Predicted Score", ascending=False)

    # prepare each subgroup
    def prep(group):
        sub = df[df["Position Group"] == group][
            ["Name", "Draft Year", "Predicted Score", "Actual Tier"]
        ].copy()
        sub["Actual Tier"]    = sub["Actual Tier"].fillna("").astype(str)
        sub["Draft Year"]     = sub["Draft Year"].astype(int).astype(str)
        sub["Predicted Score"]= sub["Predicted Score"].map(lambda x: f"{x:.3f}")
        return sub.reset_index(drop=True)

    guards = prep("Guard")
    wings  = prep("Wing")
    bigs   = prep("Big")

    # print each group with aligned columns
    print_group("Guards", guards)
    print_group("Wings",  wings)
    print_group("Bigs",   bigs)

    # then feature importances
    print_importances("Guards", GUARD_IMPORTANCES)
    print_importances("Wings",  WING_IMPORTANCES)
    print_importances("Bigs",   BIG_IMPORTANCES)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all_predictions.csv")