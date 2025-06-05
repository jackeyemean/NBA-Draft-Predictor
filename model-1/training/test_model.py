import pandas as pd
import joblib

# Load model
model = joblib.load("models/no_2014.pkl")

# Load test data
df = pd.read_csv("data/drafts_2014_cleaned.csv")  # replace with your actual file

# Drop non-feature columns
non_features = ["Name", "NBA Career Score"]
X = df.drop(columns=[col for col in non_features if col in df.columns])

# Predict
predictions = model.predict(X)

# Insert prediction at the front of the DataFrame
df.insert(0, "Predicted NBA Career Score", predictions)

# Save result
df.to_csv("data/drafts_2014_predictions.csv", index=False)
print("Predictions saved to data/drafts_2014_predictions.csv")
