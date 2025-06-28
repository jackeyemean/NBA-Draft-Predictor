import pandas as pd
import numpy as np
import joblib
import re

# ─── Configuration ─────────────────────────────────────────────────────
TEST_YEARS        = [2025]
TEST_PATH         = "web/draft-2025.csv"
GUARD_MODEL_PATH  = "web/models/guards.pkl"
WING_MODEL_PATH   = "web/models/wings.pkl"
BIG_MODEL_PATH    = "web/models/bigs.pkl"
OUTPUT_CSV        = "web/predictions_2025.csv"

# ─── Position Predicates ────────────────────────────────────────────────
def is_guard_only(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    return all(p in {"PG", "SG"} for p in parts if p)

def is_wing(pos_str: str) -> bool:
    parts = [p for p in re.split(r"[,\-/\s]+", pos_str.upper()) if p]
    if "C" in parts: return False
    if "SF" in parts: return True
    return "PF" in parts and len(parts) > 1

def is_big(pos_str: str) -> bool:
    parts = [p for p in re.split(r"[,\-/\s]+", pos_str.upper()) if p]
    return "C" in parts or all(p == "PF" for p in parts)

# ─── Feature Lists ───────────────────────────────────────────────────────
FEATURES_GUARDS = [
        "Age", "Height", "BMI",
        "CT_Win%", "CT_SOS",

        "C_GS%", "C_MPG", "C_FG%", "C_3P%", "C_FT%", "C_TS%",
        
        "C_AST_TO",

        "C_AST%", "C_TOV%", "C_USG%",

        "C_OBPM", "C_OWS",

        "C_FGA/40", "C_3PA/40", "C_FTA/40",
        "C_AST/40", "C_STL/40", "C_TOV/40", "C_PTS/40"
]
FEATURES_WINGS = [
        "Age", "Height", "BMI",
        "CT_Win%", "CT_SOS",

        "C_GS%", "C_MPG", "C_TS%", "C_TS%",
        
        "C_AST_TO", "C_ORB_DRB",

        "C_TRB%", "C_USG%",

        "C_BPM", "C_WS",

        "C_FGA/40", "C_3PA/40", "C_FTA/40", "C_TRB/40",
        "C_AST/40", "C_TOV/40", "C_PTS/40"
]
FEATURES_BIGS = [
        "Age", "Height", "BMI",
        "CT_Win%", "CT_SOS",

        "C_GS%", "C_MPG", "C_FG%", "C_FT%", "C_TS%",
        
        "C_ORB_DRB",

        "C_BLK%", "C_TRB%", "C_USG%",

        "C_DBPM", "C_DWS",

        "C_FGA/40", "C_FTA/40", "C_TRB/40",
        "C_STL/40", "C_BLK/40", "C_PTS/40"
]

# ─── Main ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df_test = pd.read_csv(TEST_PATH)
    df_test = df_test[df_test["Draft Year"].isin(TEST_YEARS)].reset_index(drop=True)

    parts = []
    for name, pred_fn, feats, mpath in [
        ("Guard", is_guard_only, FEATURES_GUARDS, GUARD_MODEL_PATH),
        ("Wing", is_wing, FEATURES_WINGS, WING_MODEL_PATH),
        ("Big",  is_big,  FEATURES_BIGS,   BIG_MODEL_PATH)
    ]:
        df_grp = df_test[df_test["POS"].apply(pred_fn)].reset_index(drop=True)
        print(f"Loading model for {name}s from {mpath}...")
        model = joblib.load(mpath)

        feat_names = list(model.feature_names_in_)
        missing = set(feat_names) - set(df_grp.columns)
        if missing:
            raise KeyError(f"Missing cols for {name} test: {missing}")

        X_test = df_grp[feat_names]
        preds = model.predict(X_test)

        df_grp["Predicted Score"] = preds
        df_grp["Actual Tier"]     = np.nan
        df_grp["Position Group"]  = name
        parts.append(df_grp[["Name", "Draft Year", "Pick Number", "POS", "Predicted Score", "Actual Tier", "Position Group"]])

    all_df = pd.concat(parts, ignore_index=True)
    all_df.sort_values(["Draft Year", "Predicted Score"], ascending=[True, False], inplace=True)
    all_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved predictions to {OUTPUT_CSV}")
