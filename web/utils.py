import joblib
import pandas as pd

GUARD_MODEL_PATH = "models/guards.pkl"

GUARD_FEATURES = [
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

def predict_score(form_data) -> float:
    model = joblib.load(GUARD_MODEL_PATH)
    
    input_data = {}
    for feature in GUARD_FEATURES:
        val = float(form_data[feature])
        if feature == "Height":  # inches → cm
            val *= 2.54
        elif feature == "Weight":  # lbs → kg
            val *= 0.453592
        input_data[feature] = val

    df = pd.DataFrame([input_data])  # single-row DataFrame
    prediction = model.predict(df)[0]
    return round(prediction, 2)
