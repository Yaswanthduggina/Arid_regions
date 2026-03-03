import requests, json, os

stations = {
    "jaisalmer": {"lat": 26.91, "lon": 70.91},
    "bikaner":   {"lat": 28.02, "lon": 73.31},
    "jodhpur":   {"lat": 26.24, "lon": 73.02},
    "barmer":    {"lat": 25.75, "lon": 71.38}
}

base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
parameter = "ALLSKY_SFC_SW_DWN"

for city, coord in stations.items():
    print(f"\nDownloading Rs for {city}")

    city_data = {}

    for year in range(2001, 2026):
        params = {
            "parameters": parameter,
            "community": "AG",
            "latitude": coord["lat"],
            "longitude": coord["lon"],
            "start": year,
            "end": year,
            "format": "JSON"
        }

        r = requests.get(base_url, params=params)
        yearly = r.json()["properties"]["parameter"][parameter]
        city_data.update(yearly)

    out_path = f"data/raw/{city}_data/{city}_Rs_hourly.json"
    with open(out_path, "w") as f:
        json.dump(city_data, f)

    print("✔ Done")
