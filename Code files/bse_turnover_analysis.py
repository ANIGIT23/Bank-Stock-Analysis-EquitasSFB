import pandas as pd

def load_and_clean_bse(file_path):
    # BSE files are CSVs
    df = pd.read_csv(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Mapping for BSE specific columns
    mapping = {}
    for col in df.columns:
        if 'date' in col.lower(): mapping[col] = 'Date'
        if 'turnover' in col.lower(): mapping[col] = 'Total Turnover'
        if 'close price' in col.lower(): mapping[col] = 'Close Price'
        if 'no.of shares' in col.lower() or 'no of shares' in col.lower(): mapping[col] = 'No of Shares'
    
    df = df[list(mapping.keys())].rename(columns=mapping)
    # Robust parsing for different BSE date formats (30-March-2026 and 30-Mar-26)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # CONVERT TO LAKHS
    df['Total Turnover (Lakhs)'] = pd.to_numeric(df['Total Turnover'], errors='coerce') / 100000
    return df.sort_values('Date')

# Load raw data
df_eq_bse = load_and_clean_bse("EQUITAS BSE (1-4-23 - 31-03-26).csv")
df_uj_bse = load_and_clean_bse("UJJIVAN BSE (1-4-23 - 31-03-26).csv")

def get_averages(df):
    df_idx = df.set_index('Date')
    # Weekly average (Monday start)
    weekly = df_idx.resample('W-MON')['Total Turnover (Lakhs)'].mean().reset_index()
    weekly.columns = ['Date', 'Avg Turnover (Weekly Lakhs)']
    # Monthly average (Month start)
    monthly = df_idx.resample('MS')['Total Turnover (Lakhs)'].mean().reset_index()
    monthly.columns = ['Date', 'Avg Turnover (Monthly Lakhs)']
    # Yearly average (Year start)
    yearly = df_idx.resample('YS')['Total Turnover (Lakhs)'].mean().reset_index()
    yearly.columns = ['Date', 'Avg Turnover (Yearly Lakhs)']
    return weekly, monthly, yearly

eq_w, eq_m, eq_y = get_averages(df_eq_bse)
uj_w, uj_m, uj_y = get_averages(df_uj_bse)

# Merge and Save
output_file = "BSE_Turnover_Analysis.xlsx"
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    pd.merge(eq_w, uj_w, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Weekly_Analysis', index=False)
    pd.merge(eq_m, uj_m, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Monthly_Analysis', index=False)
    pd.merge(eq_y, uj_y, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Yearly_Analysis', index=False)
    # Raw Data Sheets
    df_eq_bse[['Date', 'Close Price', 'No of Shares', 'Total Turnover (Lakhs)']].to_excel(writer, sheet_name='Equitas_Raw', index=False)
    df_uj_bse[['Date', 'Close Price', 'No of Shares', 'Total Turnover (Lakhs)']].to_excel(writer, sheet_name='Ujjivan_Raw', index=False)

print(f"BSE Turnover Analysis report saved as {output_file}")
