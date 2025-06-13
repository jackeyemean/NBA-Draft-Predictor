import pandas as pd
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("model-4/data/populated-2011-2021.csv")  # Replace with actual path

# career score calculation
df['raw_score'] = (
    0.5 * df['NBA_GS%'] +
    0.3 * df['NBA_PTS/G'] +
    0.2 * df['NBA_AST/G'] +
    0.2 * df['NBA_TRB/G']
).round(2)

# normalize 1–100
scaler = MinMaxScaler(feature_range=(1, 100))
df['Career Score'] = scaler.fit_transform(df[['raw_score']]).round(2)

def map_to_tier(row):
    if row['NBA_seasons'] <= 2:
        return 0.0  # scrub
    score = row['Career Score']
    if score < 26:
        return 0.5  # deep bench
    elif score < 46:
        return 1.0  # bench
    elif score < 64:
        return 2.5  # role player
    elif score < 80:
        return 3.0  # starter
    elif score < 90:
        return 4  # strong starter
    else:
        return 4.5  # all-Star
    # manually assign 5 - super-star 

df['Player Tier'] = df.apply(map_to_tier, axis=1)

# Save result
df.to_csv("training-data-2011-2024.csv", index=False)
