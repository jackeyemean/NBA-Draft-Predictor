# build_predictions.py
# -------------------
# Combines LOO-predicted scores for 2011–2021 with direct model predictions for 2022–2024
# into a single CSV for use in the web backend.

import pandas as pd
import numpy as np
import joblib
import re
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict

# ─── Configuration ─────────────────────────────────────────────────────
MIN_YEAR_LOO      = 2011
MAX_YEAR_LOO      = 2021
TEST_YEARS        = [2022, 2023, 2024]
TRAIN_PATH        = "model-5/data/TRAINING.csv"
TEST_PATH         = "model-5/data/TESTING.csv"
GUARD_MODEL_PATH  = "model-5/guards.pkl"
WING_MODEL_PATH   = "model-5/wings.pkl"
BIG_MODEL_PATH    = "model-5/bigs.pkl"
OUTPUT_CSV        = "all_predictions.csv"

# ─── Position Predicates ────────────────────────────────────────────────
def is_guard_only(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    GUARD_POS = {"PG", "SG"}
    return all(p in GUARD_POS for p in parts)

def is_wing(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    if "C" in parts:
        return False
    if "SF" in parts:
        return True
    if "PF" in parts and len(parts) > 1:
        return True
    return False

def is_big(pos_str: str) -> bool:
    parts = re.split(r"[,\-/\s]+", pos_str.upper())
    parts = [p for p in parts if p]
    return ("C" in parts) or all(p == "PF" for p in parts)

# ─── Feature Lists ───────────────────────────────────────────────────────
FEATURES_GUARDS = [
    "Age", "Height", "Weight", "BMI",
    "College Strength", "Seasons Played (College)",
    "CT_Win%", "CT_SRS", "CT_SOS", "CT_ORtg", "CT_DRtg",
    "C_G", "C_GS%", "C_MPG",
    "C_AST_TO",
    "C_PER", "C_TS%", "C_AST%", "C_STL%", "C_TRB%", "C_USG%", "C_TOV%",
    "C_OWS", "C_DWS", "C_ORtg", "C_DRtg", "C_WS/40", "C_OBPM", "C_DBPM", "C_BPM",
    "C_FGA/40", "C_3PA/40", "C_FTA/40", "C_TRB/40",
    "C_AST/40", "C_STL/40", "C_TOV/40", "C_PTS/40"
]
FEATURES_WINGS = [
    "Age", "Height", "Weight", "BMI",
    "College Strength", "Seasons Played (College)",
    "CT_Win%", "CT_SRS", "CT_SOS", "CT_ORtg", "CT_DRtg",
    "C_G", "C_GS%", "C_MPG",
    "C_AST_TO", "C_ORB_DRB", "C_BLK_MPG",
    "C_PER", "C_TS%", "C_AST%", "C_STL%", "C_BLK%", "C_TRB%", "C_USG%", "C_TOV%",
    "C_OWS", "C_DWS", "C_ORtg", "C_DRtg", "C_WS/40", "C_OBPM", "C_DBPM", "C_BPM",
    "C_FGA/40", "C_3PA/40", "C_FTA/40", "C_TRB/40",
    "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PTS/40"
]
FEATURES_BIGS = [
    "Age", "Height", "Weight", "BMI",
    "College Strength", "Seasons Played (College)",
    "CT_Win%", "CT_SRS", "CT_SOS", "CT_ORtg", "CT_DRtg",
    "C_G", "C_GS%", "C_MPG",
    "C_BLK_MPG", "C_ORB_DRB",
    "C_PER", "C_TS%", "C_AST%", "C_STL%", "C_TRB%", "C_USG%", "C_TOV%", "C_BLK%",
    "C_OWS", "C_DWS", "C_ORtg", "C_DRtg", "C_WS/40", "C_OBPM", "C_DBPM", "C_BPM",
    "C_FGA/40", "C_3PA/40", "C_FTA/40", "C_TRB/40",
    "C_AST/40", "C_STL/40", "C_BLK/40", "C_TOV/40", "C_PTS/40"
]

def run_loo(df, features):
    loo = LeaveOneOut()
    model = RandomForestRegressor(n_estimators=500, random_state=69, n_jobs=-1)
    X = df[features]
    y = df["Player Tier"]
    return cross_val_predict(model, X, y, cv=loo, n_jobs=-1, verbose=1)

parts = []
# LOO predictions

df_train = pd.read_csv(TRAIN_PATH)
df_train = df_train[df_train["Draft Year"].between(MIN_YEAR_LOO, MAX_YEAR_LOO)]
for name, pred_fn, feats in [("Guard", is_guard_only, FEATURES_GUARDS),
                             ("Wing", is_wing, FEATURES_WINGS),
                             ("Big", is_big, FEATURES_BIGS)]:
    df_grp = df_train[df_train["POS"].apply(pred_fn)].reset_index(drop=True)
    missing = set(feats) - set(df_grp.columns)
    if missing:
        raise KeyError(f"Missing cols for {name}: {missing}")
    print(f"Running LOO for {name}s...")
    preds = run_loo(df_grp, feats)
    df_grp["Predicted Score"] = preds
    df_grp["Actual Tier"]    = df_grp["Player Tier"]
    df_grp["Position Group"] = name
    parts.append(df_grp[["Name","Draft Year","POS","Predicted Score","Actual Tier","Position Group"]])

# Direct predictions
df_test = pd.read_csv(TEST_PATH)
df_test = df_test[df_test["Draft Year"].isin(TEST_YEARS)].reset_index(drop=True)
for name, pred_fn, feats, mpath in [("Guard", is_guard_only, FEATURES_GUARDS, GUARD_MODEL_PATH),
                                    ("Wing", is_wing, FEATURES_WINGS, WING_MODEL_PATH),
                                    ("Big", is_big, FEATURES_BIGS, BIG_MODEL_PATH)]:
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
    parts.append(df_grp[["Name","Draft Year","POS","Predicted Score","Actual Tier","Position Group"]])

all_df = pd.concat(parts, ignore_index=True)
all_df.sort_values(["Draft Year","Predicted Score"], ascending=[True,False], inplace=True)
all_df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved combined predictions to {OUTPUT_CSV}")
