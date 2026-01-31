# Project Status and Commands Used

## Data Extraction

The `scripts` folder contains several Python scripts used to download data from the NASA POWER API. The primary script is `download_T2M_for_4cities.py`, which downloads hourly data for the following parameters:

-   Mean temperature (°C) (T2M)
-   Relative humidity (%) (RH2M)
-   Wind speed at 2 m (m/s) (WS2M)
-   Incoming solar radiation (MJ/m²/hour) (ALLSKY_SFC_SW_DWN)
-   Surface pressure (kPa) (PS)

The data was downloaded for four cities: Jaisalmer, Bikaner, Jodhpur, and Barmer, for the years 2001 to 2025.

### Commands Used to Run the Scripts

The following commands were used to run the download scripts:

```bash
python scripts/download_ALLSKY_SFC_SW_DWN_for_4cities.py
python scripts/download_PS_for_4cities.py
python scripts/download_RH2M_for_4cities.py
python scripts/download_T2M_for_4cities.py
python scripts/download_WS2M_for_4cities.py
```

## Data Cleaning

The `scripts/clean_nasa_power_data.py` script is intended to clean the downloaded data. However, it is currently not functional because it points to a non-existent directory (`data/raw/nasa_power`) and is designed for monthly data, while the downloaded data is hourly. This script needs to be updated to work with the current data structure.
