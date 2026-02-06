# Research Project: ETo Calculation Workflow Documentation

This document provides an overview of the project structure, the purpose of each script, and the data processing workflow for calculating Evapotranspiration (ETo) for Rajasthan cities.

## 📂 Folder Structure

- **`data/`**: The main data repository.
    - **`raw/`**: Contains original JSON data files downloaded from NASA POWER API, organized by city (e.g., `barmer_data/`).
    - **`processed/`**: Contains intermediate CSV files where hourly data for all meteorological parameters are merged (`_hourly_merged.csv`) and cleaned (`_hourly_clean.csv`).
- **`ET0_new/`**: The final output folder containing hourly ETo calculation results (`_hourly_ETo.csv`).
- **`scripts/`**: Contains all Python scripts for downloading, processing, and calculating ETo.
- **`notes/`**: Contains analysis notes and integrity reports regarding the dataset and calculations.

---

## 📜 Scripts Overview

### 1. Data Ingestion (Downloaders)
These scripts fetch hourly meteorological data from the NASA POWER API for the years 2001–2025.
- **`download_T2M_for_4cities.py`**: Downloads air temperature at 2 meters (°C).
- **`download_RH2M_for_4cities.py`**: Downloads relative humidity at 2 meters (%).
- **`download_WS2M_for_4cities.py`**: Downloads wind speed at 2 meters (m/s).
- **`download_ALLSKY_SFC_SW_DWN_for_4cities.py`**: Downloads surface solar radiation (MJ/m²/hr).
- **`download_PS_for_4cities.py`**: Downloads surface pressure (kPa).

### 2. Data Processing & Cleaning
- **`merge_hourly_city_data.py`**: Merges the separate JSON parameter files into a single hourly CSV for each city.
- **`clean_hourly_merged.py`**: Cleans the merged data by replacing NASA fill values (-999) with NaN and applying scientific range checks (e.g., RH between 0-100%).
- **`process_data_correct.py`**: Aggregates hourly data to daily values and calculates daily ETo using the `pyet` library (FAO-56 standard).

### 3. ETo Calculations
- **`calc_ETo_corrected.py`**: **Primary script** for hourly ETo calculation. It implements the FAO-56 Penman-Monteith equation for hourly time steps, including specialized handling for night-time radiation and soil heat flux (`G`). This script outputs to the `ET0_new/` folder.
- **`calc_ETo_all_cities.py`**: An alternative or older calculation script for ETo.

### 4. Verification & Utility
- **`verify_results.py`**: Analyzes the final `ET0_new` outputs, generating monthly summaries and checking correlations between ETo and meteorological variables.
- **`add_header.py`**: A utility script for adding headers to data files (if needed).

---

## ⚙️ Data Workflow Summary

1. **Download**: Run `download_*.py` scripts to fetch raw JSON data.
2. **Merge**: Run `merge_hourly_city_data.py` to create consolidated hourly CSVs.
3. **Clean**: Run `clean_hourly_merged.py` to ensure data quality.
4. **Calculate**:
   - For **Daily** results: Run `process_data_correct.py`.
   - For **Hourly** results: Run `calc_ETo_corrected.py`.
5. **Verify**: Run `verify_results.py` to check the consistency and scientific accuracy of the outputs.
