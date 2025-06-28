import pandas as pd
import numpy as np

# ── CONFIG ─────────────────────────────────────────────────────────────────────
INPUT_CSV  = "raw-data/drafts-2025-to-2025.csv"
OUTPUT_CSV = "raw-data/drafts-2025-to-2025.csv"

df = pd.read_csv(INPUT_CSV)

# ── ENGINEERED FEATURES ─────────────────────────────────────────────────────────
# Assist-to-turnover
df['C_AST_TO'] = df['COLLEGE_AST'] / df['COLLEGE_TOV'].replace(0, np.nan)
# Offensive-rebound to defensive-rebound
df['C_ORB_DRB'] = df['COLLEGE_ORB'] / df['COLLEGE_DRB'].replace(0, np.nan)
# Blocks per min
df['C_BLK_MPG'] = df['COLLEGE_BLK'] / df['COLLEGE_MPG'].replace(0, np.nan)

# BMI (height in cm, weight in kg)
height_m = df['Height'] / 100
weight_kg = df['Weight']
df['BMI'] = weight_kg / (height_m ** 2)

# ── ROUND NUMERIC COLUMNS ───────────────────────────────────────────────────────
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].round(3)

# ── SAVE PROCESSED DATA ──────────────────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
print(f"Processed data saved to {OUTPUT_CSV} (rounded to 3 decimals)")
