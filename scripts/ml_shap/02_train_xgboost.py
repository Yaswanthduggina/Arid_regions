"""
Script 02 — Train XGBoost Models (Per City)
Uses TimeSeriesSplit (no data leakage) to evaluate, then
retrains on full data for SHAP. Saves metrics + model files.
"""
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor

# ─── Config ───────────────────────────────────────────────────────────
CITIES   = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
IN_DIR   = os.path.join("results", "ml_input")
MDL_DIR  = os.path.join("results", "models")
RES_DIR  = "results"
os.makedirs(MDL_DIR, exist_ok=True)

FEATURES = ["T", "RH", "WS", "Rs", "P"]
TARGET   = "ETo_mm_hr"
N_SPLITS = 5

XGB_PARAMS = dict(
    n_estimators   = 800,
    max_depth      = 6,
    learning_rate  = 0.05,
    subsample      = 0.8,
    colsample_bytree = 0.8,
    random_state   = 42,
    n_jobs         = -1,
    tree_method    = "hist",   # fast for large data
)

def nse(obs, sim):
    """Nash–Sutcliffe Efficiency."""
    return 1 - np.sum((obs - sim) ** 2) / np.sum((obs - obs.mean()) ** 2)

def bias(obs, sim):
    """Mean bias (sim − obs). Positive = overestimation."""
    return float(np.mean(sim - obs))

# ─── Training loop ────────────────────────────────────────────────────
all_metrics = []

for city in CITIES:
    src = os.path.join(IN_DIR, f"{city}_ml_ready.csv")
    if not os.path.exists(src):
        print(f"[SKIP] {city}: ML dataset not found. Run 01_prepare_dataset.py first.")
        continue

    df = pd.read_csv(src, parse_dates=["datetime"]).sort_values("datetime")
    X  = df[FEATURES].values
    y  = df[TARGET].values

    print(f"\n── {city.upper()} ({len(df):,} rows) ──")

    # ── TimeSeriesSplit CV ──────────────────────────────────────
    tscv = TimeSeriesSplit(n_splits=N_SPLITS)
    fold_metrics = []

    for fold, (tr_idx, te_idx) in enumerate(tscv.split(X), 1):
        model = XGBRegressor(**XGB_PARAMS)
        model.fit(X[tr_idx], y[tr_idx],
                  eval_set=[(X[te_idx], y[te_idx])],
                  verbose=False)
        y_pred = model.predict(X[te_idx])
        fold_metrics.append({
            "fold": fold,
            "R2":   round(r2_score(y[te_idx], y_pred), 4),
            "RMSE": round(np.sqrt(mean_squared_error(y[te_idx], y_pred)), 4),
            "MAE":  round(mean_absolute_error(y[te_idx], y_pred), 4),
            "NSE":  round(nse(y[te_idx], y_pred), 4),
            "Bias": round(bias(y[te_idx], y_pred), 4),
        })
        print(f"   Fold {fold}: R²={fold_metrics[-1]['R2']:.4f}  "
              f"RMSE={fold_metrics[-1]['RMSE']:.4f}  NSE={fold_metrics[-1]['NSE']:.4f}")

    fold_df = pd.DataFrame(fold_metrics)
    mean_m  = fold_df.drop(columns="fold").mean().round(4)
    print(f"   ★ Mean →  R²={mean_m['R2']:.4f}  RMSE={mean_m['RMSE']:.4f}  "
          f"MAE={mean_m['MAE']:.4f}  NSE={mean_m['NSE']:.4f}  Bias={mean_m['Bias']:.4f}")

    # ── Final model on full data for SHAP ─────────────────────
    final_model = XGBRegressor(**XGB_PARAMS)
    final_model.fit(X, y, verbose=False)

    mdl_path = os.path.join(MDL_DIR, f"{city}_xgb_model.joblib")
    joblib.dump(final_model, mdl_path)
    print(f"   ✔ Model saved → {mdl_path}")

    all_metrics.append({
        "city": city,
        "R2":   mean_m["R2"],
        "RMSE": mean_m["RMSE"],
        "MAE":  mean_m["MAE"],
        "NSE":  mean_m["NSE"],
        "Bias": mean_m["Bias"],
    })

# ── Save combined metrics ──────────────────────────────────────────────
metrics_path = os.path.join(RES_DIR, "metrics_all_cities.csv")
pd.DataFrame(all_metrics).to_csv(metrics_path, index=False)
print(f"\n✅ All metrics saved → {metrics_path}")
