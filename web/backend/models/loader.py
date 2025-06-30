import joblib
from pathlib import Path

def get_models_dir():
    return Path(__file__).parent

def load_models():
    base = get_models_dir()
    return {
        'Guards': joblib.load(base / 'guards.pkl'),
        'Wings':  joblib.load(base / 'wings.pkl'),
        'Bigs':   joblib.load(base / 'bigs.pkl'),
    }

models = load_models()
