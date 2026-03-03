import pandas as pd
import numpy as np
import os

# ===============================
# CITY DETAILS
# ===============================
cities = {
    "jaisalmer": {"lat": 26.91, "elev": 225},
    "bikaner":   {"lat": 28.02, "elev": 234},
    "jodhpur":   {"lat": 26.24, "elev": 231},
    "barmer":    {"lat": 25.75, "elev": 227}
}

sigma = 2.043e-10
albedo = 0.23
G = 0

os.makedirs("data/ETo", exist_ok=True)

for city, info in cities.items():

    print(f"\nProcessing {city}...")

    file_path = f"data/processed/{city}_hourly_clean.csv"
    df = pd.read_csv(file_path)

    # Fix datetime column name
    df.rename(columns={df.columns[0]: "datetime"}, inplace=True)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.set_index("datetime", inplace=True)
    df.columns = ["T", "RH", "WS", "Rs", "P"]

    lat_rad = np.radians(info["lat"])
    elevation = info["elev"]

    # FAO calculations
    es = 0.6108 * np.exp((17.27 * df["T"]) / (df["T"] + 237.3))
    ea = es * df["RH"] / 100
    delta = 4098 * es / ((df["T"] + 237.3) ** 2)
    gamma = 0.000665 * df["P"]

    Rns = (1 - albedo) * df["Rs"]

    doy = df.index.dayofyear
    hour = df.index.hour

    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    delta_sun = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    omega = np.pi/12 * ((hour + 0.5) - 12)

    Ra = (12 * 60 / np.pi) * 0.0820 * dr * (
        omega * np.sin(lat_rad) * np.sin(delta_sun) +
        np.cos(lat_rad) * np.cos(delta_sun) * np.sin(omega)
    )

    Rso = (0.75 + 2e-5 * elevation) * Ra

    Rnl = sigma * ((df["T"] + 273.16) ** 4) * (0.34 - 0.14 * np.sqrt(ea)) * (1.35 * (df["Rs"] / Rso) - 0.35)

    Rn = Rns - Rnl

    ETo = (
        0.408 * delta * (Rn - G) +
        gamma * (37 / (df["T"] + 273)) * df["WS"] * (es - ea)
    ) / (delta + gamma * (1 + 0.34 * df["WS"]))

    df["ETo_hourly_mm"] = ETo

    df.index.name = "datetime"
    df.to_csv(f"data/ETo/{city}_hourly_ETo.csv")

    print(f"✔ Saved → data/ETo/{city}_hourly_ETo.csv")

print("\n✅ ALL CITIES ETo CALCULATED")
