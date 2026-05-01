"""
ml_service.py — Centralized ML logic.
Loads model bundle ONCE at module level.
Used by views; never import from models.py.
"""
import os
import pickle
import numpy as np
import pandas as pd
from django.conf import settings

# ── Load model bundle once at startup ────────────────────────────────────────
_BUNDLE_PATH = os.path.join(settings.BASE_DIR, 'diabetes_project', 'diabetes_model_bundle.pkl')
_CSV_PATH    = os.path.join(settings.BASE_DIR, 'diabetes_project', 'diabetes.csv')

try:
    with open(_BUNDLE_PATH, 'rb') as f:
        _bundle = pickle.load(f)
    _model        = _bundle['model']
    _scaler       = _bundle['scaler']          # None if Random Forest
    _use_scaler   = _bundle['use_scaler']
    _zero_means   = _bundle['zero_replacements']
    MODEL_NAME    = _bundle['model_name']
    MODEL_ACCURACY = _bundle['test_accuracy']
except Exception as e:
    raise RuntimeError(f"[ml_service] Failed to load model bundle: {e}")

try:
    _df = pd.read_csv(_CSV_PATH)
    # Fix zero values using same means from training
    for col, mean_val in _zero_means.items():
        _df[col] = _df[col].replace(0, mean_val)
except Exception as e:
    raise RuntimeError(f"[ml_service] Failed to load dataset: {e}")


# ── Public API ─────────────────────────────────────────────────────────────────

def predict(input_dict: dict) -> dict:
    """
    Run prediction for a single patient.

    Args:
        input_dict: dict with keys matching feature names
                    (pregnancies, glucose, blood_pressure, skin_thickness,
                     insulin, bmi, dpf, age)

    Returns:
        {
          'label':      'Diabetic' | 'Not Diabetic',
          'confidence': 78.4,          # percent
          'risk_level': 'High' | 'Moderate' | 'Low',
          'color':      'danger' | 'warning' | 'success',
          'features':   [ordered list of floats]
        }
    """
    # Map form field names → model feature order
    features = [
        _apply_zero_fix('Glucose',       input_dict['glucose']),
        _apply_zero_fix('BloodPressure', input_dict['blood_pressure']),
        _apply_zero_fix('SkinThickness', input_dict['skin_thickness']),
        _apply_zero_fix('Insulin',       input_dict['insulin']),
        _apply_zero_fix('BMI',           input_dict['bmi']),
        input_dict['pregnancies'],
        input_dict['dpf'],
        input_dict['age'],
    ]

    # Full feature order matches training
    feature_array = np.array([
        input_dict['pregnancies'],
        _apply_zero_fix('Glucose',       input_dict['glucose']),
        _apply_zero_fix('BloodPressure', input_dict['blood_pressure']),
        _apply_zero_fix('SkinThickness', input_dict['skin_thickness']),
        _apply_zero_fix('Insulin',       input_dict['insulin']),
        _apply_zero_fix('BMI',           input_dict['bmi']),
        input_dict['dpf'],
        input_dict['age'],
    ]).reshape(1, -1)

    if _use_scaler and _scaler is not None:
        feature_array = _scaler.transform(feature_array)

    label_int  = _model.predict(feature_array)[0]
    confidence = round(float(_model.predict_proba(feature_array)[0][label_int]) * 100, 1)
    label      = 'Diabetic' if label_int == 1 else 'Not Diabetic'

    # Risk classification
    if label_int == 1:
        risk_level = 'High' if confidence >= 70 else 'Moderate'
        color      = 'danger' if confidence >= 70 else 'warning'
    else:
        risk_level = 'Low' if confidence >= 70 else 'Moderate'
        color      = 'success' if confidence >= 70 else 'warning'

    return {
        'label':      label,
        'label_int':  int(label_int),
        'confidence': confidence,
        'risk_level': risk_level,
        'color':      color,
    }


def get_risk_profiles(top_n: int = 5) -> dict:
    """
    Return top high-risk and low-risk patient records from dataset.
    """
    high = (_df[_df['Outcome'] == 1]
            .sort_values(by=['Glucose', 'BMI', 'Age'], ascending=False)
            .head(top_n)
            .to_dict(orient='records'))

    low  = (_df[_df['Outcome'] == 0]
            .sort_values(by=['Glucose', 'BMI', 'Age'], ascending=True)
            .head(top_n)
            .to_dict(orient='records'))

    return {'high_risk': high, 'low_risk': low}


def get_dataset_stats() -> dict:
    """Return summary stats for the dashboard header."""
    return {
        'total':    len(_df),
        'diabetic': int(_df['Outcome'].sum()),
        'healthy':  int((_df['Outcome'] == 0).sum()),
        'avg_glucose': round(_df['Glucose'].mean(), 1),
        'avg_bmi':     round(_df['BMI'].mean(), 1),
    }


def _apply_zero_fix(col_name: str, value: float) -> float:
    """Replace zero with dataset mean for medical columns."""
    if value == 0 and col_name in _zero_means:
        return _zero_means[col_name]
    return value
