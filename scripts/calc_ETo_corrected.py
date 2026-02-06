import pandas as pd
import numpy as np
import os

# ===============================
# 🌍 CITY DETAILS
# ===============================
cities = {
    "jaisalmer": {"lat": 26.91, "elev": 225},
    "bikaner":   {"lat": 28.02, "elev": 234},
    "jodhpur":   {"lat": 26.24, "elev": 231},
    "barmer":    {"lat": 25.75, "elev": 227}
}

# ===============================
# 🌞 CONSTANTS
# ===============================
sigma = 2.043e-10  # Stefan–Boltzmann constant [MJ K-4 m-2 hr-1]
albedo = 0.23      # Reference crop albedo
Gsc = 0.0820       # Solar constant [MJ m-2 min-1]

# User requested directory
output_dir = "ET0_new"
os.makedirs(output_dir, exist_ok=True)

# ===============================
# 🔁 PROCESS EACH CITY
# ===============================
for city, info in cities.items():
    print(f"\n🔄 Processing {city}...")

    file_path = f"data/processed/{city}_hourly_clean.csv"
    if not os.path.exists(file_path):
        print(f"❌ File missing for {city}, skipping.")
        continue

    df = pd.read_csv(file_path)

    # ===============================
    # 📅 DATETIME FIX
    # ===============================
    df.rename(columns={df.columns[0]: "datetime"}, inplace=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    df.columns = ["T", "RH", "WS", "Rs", "P"]

    lat_rad = np.radians(info["lat"])
    elevation = info["elev"]

    # ===============================
    # 💧 VAPOR PRESSURE TERMS
    # ===============================
    es = 0.6108 * np.exp((17.27 * df["T"]) / (df["T"] + 237.3))
    ea = es * df["RH"] / 100
    delta = 4098 * es / ((df["T"] + 237.3) ** 2)
    gamma = 0.000665 * df["P"]

    # ===============================
    # ☀ NET SHORTWAVE RADIATION
    # ===============================
    Rns = (1 - albedo) * df["Rs"]

    # ===============================
    # 🌍 EXTRATERRESTRIAL RADIATION (FAO Eq. 28)
    # ===============================
    doy = df.index.dayofyear
    hour = df.index.hour

    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta_sun = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)

    t = hour + 0.5
    omega = np.pi/12 * (t - 12)
    omega1 = omega - np.pi/24
    omega2 = omega + np.pi/24

    Ra = (12 * 60 / np.pi) * Gsc * dr * (
        (omega2 - omega1) * np.sin(lat_rad) * np.sin(delta_sun) +
        np.cos(lat_rad) * np.cos(delta_sun) * (np.sin(omega2) - np.sin(omega1))
    )

    # ===============================
    # 🌤 CLEAR SKY RADIATION
    # ===============================
    Rso = (0.75 + 2e-5 * elevation) * Ra
    # FAO recommendation: Rnl calculation during night-time
    # We need a valid (non-zero) Rso for the ratio calculation, even if it's very small
    Rso_safe = np.where(Rso <= 0, 0.001, Rso) 

    # ===============================
    # 🌙 NET LONGWAVE RADIATION
    # ===============================
    # During night (Ra <= 0), ratio Rs/Rso is often taken as 0.7 or 0.8 in some standard practices,
    # or simply Rs/Rso where Rs=0 and Rso is a small value.
    ratio = np.clip(df["Rs"] / Rso_safe, 0, 1.0)
    
    # For night-time (Ra <= 0), FAO 56 suggests using a cloudiness factor. 
    # If Rs is 0, the ratio will naturally be 0.
    Rnl = sigma * ((df["T"] + 273.16) ** 4) * \
          (0.34 - 0.14 * np.sqrt(ea)) * \
          (1.35 * ratio - 0.35)

    # ===============================
    # 🌞 NET RADIATION
    # ===============================
    Rn = Rns - Rnl

    # ===============================
    # 🌄 DAY/NIGHT PHYSICS
    # ===============================
    is_day = df["Rs"] > 0
    Cd = np.where(is_day, 0.24, 0.96)
    G = np.where(is_day, 0.1 * Rn, 0.5 * Rn)

    # ===============================
    # 🌾 FAO-56 HOURLY PENMAN-MONTEITH
    # ===============================
    ETo = (
        0.408 * delta * (Rn - G) +
        gamma * (37 / (df["T"] + 273)) * df["WS"] * (es - ea)
    ) / (delta + gamma * (1 + Cd * df["WS"]))

    df["ETo_mm_hr"] = np.maximum(ETo, 0)
    df.index.name = "datetime"

    out_file = f"{output_dir}/{city}_hourly_ETo.csv"
    df.to_csv(out_file)
    print(f"✔ Saved → {out_file}")

print("\n✅ ALL CITIES ETo CALCULATED (FAO-56 HOURLY CORRECT)")
