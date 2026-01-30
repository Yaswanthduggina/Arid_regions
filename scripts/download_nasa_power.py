import requests
import json
import os

stations = {
    "jaisalmer": {"lat": 26.91, "lon": 70.91},
    "bikaner":   {"lat": 28.02, "lon": 73.31},
    "jodhpur":   {"lat": 26.24, "lon": 73.02},
    "barmer":    {"lat": 25.75, "lon": 71.38}
}

base_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# 🔥 FULL FAO-56 DATASET
parameters = ",".join([
    "T2M",            # Mean temp
    "T2M_MAX",        # Max temp
    "T2M_MIN",        # Min temp
    "RH2M",           # Humidity
    "WS2M",           # Wind speed
    "ALLSKY_NET_SW_DWN",  # Net shortwave radiation
    "PS"              # Surface pressure
])

start_year = 2001
end_year = 2025

output_dir = "data/raw/nasa_power"
os.makedirs(output_dir, exist_ok=True)

for city, coord in stations.items():
    print(f"Downloading full FAO dataset for {city}...")

    params = {
        "parameters": parameters,
        "community": "AG",
        "latitude": coord["lat"],
        "longitude": coord["lon"],
        "start": start_year,
        "end": end_year,
        "format": "JSON"
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(f"Download failed for {city}")

    data = response.json()

    with open(f"{output_dir}/{city}_fao56.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved {city}_fao56.json")

print("✅ COMPLETE FAO-56 DATA ACQUIRED")
