import pandas as pd

# Load predictions
df = pd.read_csv("data/test_data_with_predictions.csv")

# Check required columns
if "Predicted NBA Career Score" not in df.columns:
    raise ValueError("Column 'Predicted NBA Career Score' not found in CSV.")
if "Name" not in df.columns:
    raise ValueError("Column 'Name' not found in CSV.")

# Sort by predicted score
df_sorted = df.sort_values(by="Predicted NBA Career Score", ascending=False)

# Print top-ranked players
print("\n=== Ranked Players by Predicted NBA Career Score ===\n")
for i, row in df_sorted.iterrows():
    print(f"{row['Name']:30} | Score: {row['Predicted NBA Career Score']:.2f}")
