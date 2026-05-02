"""
ml_service.py — Loads BOTH disease model bundles once at startup.
"""
import os, pickle
import numpy as np
import pandas as pd
from django.conf import settings

BASE = settings.BASE_DIR

def _load(fname):
    path = os.path.join(BASE, 'diabetes_project', fname)
    with open(path, 'rb') as f:
        return pickle.load(f)

try:
    _db  = _load('diabetes_model_bundle.pkl')
    _hrt = _load('heart_model_bundle.pkl')
except Exception as e:
    raise RuntimeError(f"[ml_service] Cannot load model bundles: {e}")

# ── Public constants ──────────────────────────────────────────────────────────
DIAB_MODEL_NAME = _db['model_name']
DIAB_ACCURACY   = _db['test_accuracy']
DIAB_AUC        = _db.get('roc_auc', 0)
HEART_MODEL_NAME= _hrt['model_name']
HEART_ACCURACY  = _hrt['test_accuracy']
HEART_AUC       = _hrt.get('roc_auc', 0)

# ── Load CSVs once ────────────────────────────────────────────────────────────
_diab_csv  = os.path.join(BASE, 'diabetes_project', 'diabetes.csv')
_heart_csv = os.path.join(BASE, 'diabetes_project', 'heart_disease.csv')

_df_diab  = pd.read_csv(_diab_csv)
_df_heart = pd.read_csv(_heart_csv)

# fix zeros in diabetes csv
for col, mean_val in _db['zero_replacements'].items():
    if col in _df_diab.columns:
        _df_diab[col] = _df_diab[col].replace(0, mean_val)

# ── Reference ranges for risk indicator colouring ────────────────────────────
DIAB_RANGES = {
    'glucose':        {'ok': (70, 100),  'warn': (100, 125), 'label': 'mg/dL'},
    'blood_pressure': {'ok': (60, 80),   'warn': (80, 90),   'label': 'mm Hg'},
    'bmi':            {'ok': (18.5, 25), 'warn': (25, 30),   'label': 'kg/m²'},
    'insulin':        {'ok': (16, 166),  'warn': (166, 300), 'label': 'mu U/ml'},
    'age':            {'ok': (1, 45),    'warn': (45, 60),   'label': 'yrs'},
}
HEART_RANGES = {
    'age':      {'ok': (1, 45),    'warn': (45, 65),   'label': 'yrs'},
    'trestbps': {'ok': (90, 120),  'warn': (120, 140), 'label': 'mm Hg'},
    'chol':     {'ok': (0, 200),   'warn': (200, 240), 'label': 'mg/dL'},
    'thalach':  {'ok': (130, 210), 'warn': (100, 130), 'label': 'bpm'},
    'oldpeak':  {'ok': (0, 1.0),   'warn': (1.0, 2.5), 'label': 'mm'},
}


def _risk_color(field, value, ranges):
    if field not in ranges:
        return 'neutral'
    r = ranges[field]
    lo, hi = r['ok']
    if lo <= value <= hi:
        return 'ok'
    wlo, whi = r['warn']
    if wlo <= value <= whi:
        return 'warn'
    return 'danger'


def _outcome(label_int, confidence):
    label = 'Diabetic' if label_int == 1 else 'Not Diabetic'
    if label_int == 1:
        risk  = 'High' if confidence >= 70 else 'Moderate'
        color = 'danger' if confidence >= 70 else 'warning'
    else:
        risk  = 'Low'  if confidence >= 70 else 'Moderate'
        color = 'success' if confidence >= 70 else 'warning'
    return {'label': label, 'label_int': int(label_int),
            'confidence': confidence, 'risk_level': risk, 'color': color}


# ── DIABETES PREDICTION ───────────────────────────────────────────────────────
def predict_diabetes(d):
    zm = _db['zero_replacements']
    def zf(col, v): return zm.get(col, v) if v == 0 else v

    g   = zf('Glucose', d['glucose'])
    bp  = zf('BloodPressure', d['blood_pressure'])
    st  = zf('SkinThickness', d['skin_thickness'])
    ins = zf('Insulin', d['insulin'])
    bmi = zf('BMI', d['bmi'])
    age = d['age']

    arr = np.array([[
        d['pregnancies'], g, bp, st, ins, bmi,
        d['dpf'], age,
        g * age / 1000,       # GlucoseAge
        bmi * age / 1000,     # BMIAge
        ins / (g + 1),        # InsulinGlucose
    ]])

    m = _db['model']
    s = _db['scaler']
    if _db['use_scaler'] and s:
        arr = s.transform(arr)

    li   = m.predict(arr)[0]
    conf = round(float(m.predict_proba(arr)[0][li]) * 100, 1)
    res  = _outcome(li, conf)

    # risk indicators per field
    fields = {
        'glucose': g, 'blood_pressure': bp, 'bmi': bmi,
        'insulin': ins, 'age': age,
    }
    res['indicators'] = {k: _risk_color(k, v, DIAB_RANGES) for k, v in fields.items()}
    res['feature_importance'] = _db['feature_importance']

    # radar: patient vs mean (8 core features)
    means = {
        'Glucose': _df_diab['Glucose'].mean(), 'BloodPressure': _df_diab['BloodPressure'].mean(),
        'SkinThickness': _df_diab['SkinThickness'].mean(), 'Insulin': _df_diab['Insulin'].mean(),
        'BMI': _df_diab['BMI'].mean(), 'Pregnancies': _df_diab['Pregnancies'].mean(),
        'DPF': _df_diab['DiabetesPedigreeFunction'].mean(), 'Age': _df_diab['Age'].mean(),
    }
    patient_vals = [g, bp, st, ins, bmi, d['pregnancies'], d['dpf'], age]
    mean_vals    = list(means.values())
    # normalise 0-1 for radar
    maxs = [300, 122, 99, 846, 67, 17, 2.42, 81]
    res['radar'] = {
        'labels':  list(means.keys()),
        'patient': [round(v/m, 3) for v,m in zip(patient_vals, maxs)],
        'average': [round(v/m, 3) for v,m in zip(mean_vals, maxs)],
    }
    return res


# ── HEART DISEASE PREDICTION ──────────────────────────────────────────────────
def predict_heart(d):
    arr = np.array([[
        d['age'], d['sex'], d['cp'], d['trestbps'], d['chol'],
        d['fbs'], d['restecg'], d['thalach'], d['exang'],
        d['oldpeak'], d['slope'], d['ca'], d['thal'],
    ]])

    m = _hrt['model']
    s = _hrt['scaler']
    if _hrt['use_scaler'] and s:
        arr = s.transform(arr)

    li   = m.predict(arr)[0]
    conf = round(float(m.predict_proba(arr)[0][li]) * 100, 1)
    res  = dict(_outcome(li, conf))
    res['label'] = 'Heart Disease' if li == 1 else 'No Disease'

    fields = {
        'age': d['age'], 'trestbps': d['trestbps'],
        'chol': d['chol'], 'thalach': d['thalach'], 'oldpeak': d['oldpeak'],
    }
    res['indicators'] = {k: _risk_color(k, v, HEART_RANGES) for k, v in fields.items()}
    res['feature_importance'] = _hrt['feature_importance']

    means = {col: round(_df_heart[col].mean(), 2) for col in
             ['age','trestbps','chol','thalach','oldpeak','ca']}
    patient_vals = [d['age'], d['trestbps'], d['chol'],
                    d['thalach'], d['oldpeak'], d['ca']]
    mean_vals    = list(means.values())
    maxs         = [80, 200, 400, 210, 6.2, 3]
    res['radar'] = {
        'labels':  list(means.keys()),
        'patient': [round(v/m, 3) for v,m in zip(patient_vals, maxs)],
        'average': [round(v/m, 3) for v,m in zip(mean_vals, maxs)],
    }
    return res


# ── PROFILES & STATS ──────────────────────────────────────────────────────────
def get_diabetes_profiles(n=5):
    high = (_df_diab[_df_diab['Outcome']==1]
            .sort_values(['Glucose','BMI','Age'], ascending=False).head(n).to_dict('records'))
    low  = (_df_diab[_df_diab['Outcome']==0]
            .sort_values(['Glucose','BMI','Age'], ascending=True).head(n).to_dict('records'))
    return high, low

def get_heart_profiles(n=5):
    b = _hrt.get('high_risk', [])
    g = _hrt.get('low_risk',  [])
    return b, g

def get_diabetes_stats():
    return {
        'total':       len(_df_diab),
        'diabetic':    int(_df_diab['Outcome'].sum()),
        'healthy':     int((_df_diab['Outcome']==0).sum()),
        'avg_glucose': round(_df_diab['Glucose'].mean(), 1),
        'avg_bmi':     round(_df_diab['BMI'].mean(), 1),
        'dataset_size': _db['dataset_size'],
    }

def get_heart_stats():
    s = _hrt.get('dataset_stats', {})
    s['dataset_size'] = _hrt['dataset_size']
    return s

def get_diab_chart_data():
    """Glucose & BMI distribution split by outcome for bar charts."""
    bins_gluc = list(range(50, 310, 30))
    bins_bmi  = [10, 18.5, 25, 30, 35, 40, 50]
    def hist(series, bins):
        counts, edges = np.histogram(series, bins=bins)
        labels = [f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges)-1)]
        return labels, counts.tolist()

    d0 = _df_diab[_df_diab['Outcome']==0]
    d1 = _df_diab[_df_diab['Outcome']==1]

    gl, g0 = hist(d0['Glucose'], bins_gluc)
    _,  g1 = hist(d1['Glucose'], bins_gluc)
    bl, b0 = hist(d0['BMI'],     bins_bmi)
    _,  b1 = hist(d1['BMI'],     bins_bmi)

    return {
        'glucose': {'labels': gl, 'healthy': g0, 'diabetic': g1},
        'bmi':     {'labels': bl, 'healthy': b0, 'diabetic': b1},
        'diab_fi': sorted(_db['feature_importance'].items(),  key=lambda x:-x[1])[:8],
        'heart_fi': sorted(_hrt['feature_importance'].items(), key=lambda x:-x[1])[:8],
    }
