import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv("data/drafts.csv")

IGNORE_YEARS = [2014]
if "Draft Year" in df.columns:
    df = df[~df["Draft Year"].isin(IGNORE_YEARS)]

FEATURES = [
    "Age", "Height", "Weight", "NBA Relatives", "Seasons Played (College)",
    "G", "GS%", "MPG", "PER", "TS%", "ORB%", "DRB%", "TRB%", "AST%", "STL%", "BLK%", "TOV%", "USG%", "WS/40", "BPM",
    "FG/100", "FGA/100", "3P/100", "3PA/100", "FT/100", "FTA/100", "ORB/100", "DRB/100", "TRB/100", "AST/100", "STL/100", "BLK/100", "TOV/100", "PF/100", "PTS/100", "ORtg", "DRtg"
]
missing_cols = [col for col in FEATURES if col not in df.columns]
if missing_cols:
    raise KeyError(f"Missing required columns: {missing_cols}")

# target and features
y = df["NBA Career Score"]
X = df[FEATURES]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# print performance
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse:.2f}")
print(f"R² Score: {r2:.2f}")

# save model
joblib.dump(model, "models/model_excluding_years.pkl")
print("Model saved to models/model_excluding_years.pkl")