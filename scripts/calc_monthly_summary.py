import pandas as pd
import os
import glob

# Directory setup
INPUT_DIR = "ET0_new"
OUTPUT_DIR = "data"
files = glob.glob(os.path.join(INPUT_DIR, "*_hourly_ETo.csv"))

all_summaries = []

print("🔄 Calculating Monthly ETo for all cities...")

for file in files:
    city = os.path.basename(file).split('_')[0]
    print(f"  Processing {city}...")
    
    # Load hourly data
    df = pd.read_csv(file)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    # Resample to Monthly and sum ETo
    monthly = df['ETo_mm_hr'].resample('ME').sum().to_frame()
    monthly.columns = ['Total_ETo_mm']
    monthly['City'] = city
    
    all_summaries.append(monthly.reset_index())

# Combine all cities
if all_summaries:
    final_monthly_report = pd.concat(all_summaries)
    
    # Pivot: Years/Months as rows, Cities as columns
    # We'll create a Date column for easier reading
    pivot_report = final_monthly_report.pivot(index='datetime', columns='City', values='Total_ETo_mm')
    
    # Save results
    summary_path = os.path.join(OUTPUT_DIR, "eto_monthly_summary_pivot.csv")
    pivot_report.to_csv(summary_path)
    print(f"\n✅ Monthly summary saved to {summary_path}")
    
    # Display a sample (last 12 months)
    print("\n--- Monthly ETo Summary (Last 12 Months - mm/month) ---")
    print(pivot_report.tail(12).round(2))
else:
    print("❌ No data files found in ET0_new.")
