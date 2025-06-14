import pandas as pd
import numpy as np

# ── CONFIG ─────────────────────────────────────────────────────────────────────
INPUT_CSV  = "model-4/data/training-2011-2021.csv"
OUTPUT_CSV = "model-4/data/final-training.csv"

df = pd.read_csv(INPUT_CSV)

# ── ENGINEERED FEATURES ─────────────────────────────────────────────────────────
# Assist-to-turnover
df['C_AST_TO'] = df['C_AST'] / df['C_TOV'].replace(0, np.nan)
# Offensive-rebound to defensive-rebound
df['C_ORB_DRB'] = df['C_ORB'] / df['C_DRB'].replace(0, np.nan)
# Blocks per min
df['C_BLK_MPG'] = df['C_BLK'] / df['C_MPG'].replace(0, np.nan)

# BMI (height in cm, weight in kg)
height_m = df['Height'] / 100
weight_kg = df['Weight']
df['BMI'] = weight_kg / (height_m ** 2)

# ── MAIN POSITION EXTRACTION & ENCODING ─────────────────────────────────────────
# Extract primary position (e.g., 'PG,SG' -> 'PG')
df['Main_POS'] = df['POS'].apply(lambda x: x.split(',')[0].strip())
# One-hot encode Main_POS into separate columns: Main_POS_PG, Main_POS_SG, etc.
pos_dummies = pd.get_dummies(df['Main_POS'], prefix='Main_POS')
df = pd.concat([df, pos_dummies], axis=1)

# drop Main_POS column
df.drop(columns=['Main_POS'], inplace=True)

# ── ROUND NUMERIC COLUMNS ───────────────────────────────────────────────────────
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].round(3)

# ── SAVE PROCESSED DATA ──────────────────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
print(f"Processed data saved to {OUTPUT_CSV} (rounded to 3 decimals)")
