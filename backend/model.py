import pandas as pd
import numpy as np
import joblib
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_FILE = "rf_model.pkl"

# ---------------- Helper: Convert Trainset list to DataFrame ---------------- #
def fleet_to_df(fleet_list):
    """
    Converts a list of Trainset objects to a pandas DataFrame ready for ML model.
    """
    data = []
    for ts in fleet_list:
        data.append({
            "train_id": ts.train_id,
            "fitness_rolling_days": ts.fitness_rolling_valid,
            "fitness_signalling_days": ts.fitness_signalling_valid,
            "fitness_telecom_days": ts.fitness_telecom_valid,
            "job_cards_open": ts.job_cards_open,
            "branding_hours_needed": ts.branding_hours_left,
            "current_mileage": ts.current_mileage,
            "cleaning_slots_needed": ts.cleaning_slots_needed,
            "min_shunt_cost": min(ts.shunt_cost_to_bays.values())
        })
    return pd.DataFrame(data)

# ---------------- Train RandomForest Model ---------------- #
def train_ml_model(fleet_list, outcomes_history=None):
    """
    Train RandomForest to predict withdrawal/failure risk.
    fleet_list: list of Trainset objects
    outcomes_history: list of dicts with keys 'train_id' + outcome(1/0)
    """
    df_assignments = fleet_to_df(fleet_list)

    if not outcomes_history:
        df_assignments['outcome'] = np.random.choice([0,1], size=len(df_assignments))
    else:
        df_out = pd.DataFrame(outcomes_history)
        df_assignments = df_assignments.merge(df_out[['train_id','outcome']], on='train_id', how='left')
        df_assignments['outcome'] = df_assignments['outcome'].fillna(1)

    features = ['fitness_rolling_days','fitness_signalling_days','fitness_telecom_days',
                'job_cards_open','branding_hours_needed','current_mileage',
                'cleaning_slots_needed','min_shunt_cost']

    X = df_assignments[features]
    y = df_assignments['outcome']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    joblib.dump(clf, MODEL_FILE)
    return clf

# ---------------- Predict withdrawal/failure risk ---------------- #
def predict_withdrawal_risk(fleet_list):
    """
    Returns a dict: {train_id: probability_of_failure}
    """
    df_assignments = fleet_to_df(fleet_list)

    try:
        clf = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        return {ts.train_id: 0.0 for ts in fleet_list}

    features = ['fitness_rolling_days','fitness_signalling_days','fitness_telecom_days',
                'job_cards_open','branding_hours_needed','current_mileage',
                'cleaning_slots_needed','min_shunt_cost']

    X = df_assignments[features]
    probs = clf.predict_proba(X)[:,1]  # probability of failure=1
    return {tid: float(p) for tid,p in zip(df_assignments['train_id'], probs)}

# ---------------- SHAP Explainability ---------------- #
def shap_explain(fleet_list, train_id):
    """
    Returns SHAP values for a given train_id
    """
    df_assignments = fleet_to_df(fleet_list)
    try:
        clf = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        return {}

    features = ['fitness_rolling_days','fitness_signalling_days','fitness_telecom_days',
                'job_cards_open','branding_hours_needed','current_mileage',
                'cleaning_slots_needed','min_shunt_cost']

    X = df_assignments[features]
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X)

    idx_list = df_assignments.index[df_assignments['train_id']==train_id].tolist()
    if not idx_list:
        return {}
    idx = idx_list[0]

    shap_dict = {f: float(shap_values[1][idx][i]) for i,f in enumerate(features)}
    return shap_dict
