"""
Script 01 — Prepare ML Dataset
Loads hourly ETo CSVs from ET0_new/, adds temporal features,
filters meaningful rows, saves ML-ready CSVs to results/ml_input/.
"""
import pandas as pd
import os

# ─── Config ───────────────────────────────────────────────────────────
CITIES = ["barmer", "bikaner", "jaisalmer", "jodhpur"]
ETO_DIR = "ET0_new"
OUT_DIR = os.path.join("results", "ml_input")
os.makedirs(OUT_DIR, exist_ok=True)

FEATURES = ["T", "RH", "WS", "Rs", "P"]
TARGET   = "ETo_mm_hr"

def assign_season(month):
    """Assign climatological season for Rajasthan."""
    if month in [4, 5, 6]:   return "Summer"
    elif month in [7, 8, 9]: return "Monsoon"
    elif month in [10, 11]:  return "Post-Monsoon"
    else:                    return "Winter"  # Dec, Jan, Feb, Mar

# ─── Process each city ────────────────────────────────────────────────
summary = []

for city in CITIES:
    src = os.path.join(ETO_DIR, f"{city}_hourly_ETo.csv")
    if not os.path.exists(src):
        print(f"[SKIP] Missing: {src}")
        continue

    df = pd.read_csv(src, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)

    # Ensure correct column names
    df.columns = [c.strip() for c in df.columns]

    # Drop rows with missing values in features or target
    df = df[FEATURES + [TARGET]].dropna()

    # Filter: keep only rows where ETo is positive (physical daytime activity)
    # Night rows (ETo=0, Rs=0) are not informative for SHAP interpretability
    df = df[df[TARGET] > 0].copy()

    # ── Temporal features ──────────────────────────────────────
    df["month"]  = df.index.month
    df["hour"]   = df.index.hour
    df["season"] = df["month"].apply(assign_season)
    df["year"]   = df.index.year

    # Save
    out_path = os.path.join(OUT_DIR, f"{city}_ml_ready.csv")
    df.to_csv(out_path)

    n = len(df)
    eto_mean = df[TARGET].mean()
    eto_max  = df[TARGET].max()
    summary.append({"city": city, "n_rows": n,
                    "eto_mean_mm_hr": round(eto_mean, 4),
                    "eto_max_mm_hr":  round(eto_max,  4)})
    print(f"[OK] {city:10s} → {n:,} rows | ETo mean={eto_mean:.3f}, max={eto_max:.3f}")

# Save summary
pd.DataFrame(summary).to_csv(os.path.join(OUT_DIR, "dataset_summary.csv"), index=False)
print(f"\n✅ ML datasets saved → {OUT_DIR}")
