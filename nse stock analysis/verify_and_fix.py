import pandas as pd

def load_and_clean(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {}
    for col in df.columns:
        if 'date' in col.lower(): mapping[col] = 'Date'
        if 'turnover' in col.lower(): mapping[col] = 'Total Turnover'
    
    # Selection and conversion
    df = df[list(mapping.keys())].rename(columns=mapping)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Turnover (Lakhs)'] = pd.to_numeric(df['Total Turnover'], errors='coerce') / 100000
    return df

df_eq = load_and_clean("EQUITAS NSE (1-4-23 - 31-03-26).xlsx")

# --- MANUAL VERIFICATION SAMPLE ---
# First week of March 2026
sample = df_eq[(df_eq['Date'] >= '2026-03-02') & (df_eq['Date'] <= '2026-03-06')]
vals = sample['Turnover (Lakhs)'].tolist()
calc_avg = sum(vals) / len(vals)

print("--- Manual Verification: March 2nd - 6th, 2026 (Equitas) ---")
for d, v in zip(sample['Date'].dt.date, vals):
    print(f"Date: {d}, Turnover: {v:.2f} Lakhs")
print(f"\nFormula: ({' + '.join([f'{v:.2f}' for v in vals])}) / {len(vals)}")
print(f"Calculated Average: {calc_avg:.2f} Lakhs")

# Fixing Labels for Excel
def get_averages_fixed(df):
    df_idx = df.set_index('Date')
    weekly = df_idx.resample('W-MON')['Turnover (Lakhs)'].mean().reset_index()
    monthly = df_idx.resample('MS')['Turnover (Lakhs)'].mean().reset_index()
    yearly = df_idx.resample('YS')['Turnover (Lakhs)'].mean().reset_index()
    return weekly, monthly, yearly

df_uj = load_and_clean("UJJIVAN NSE (1-4-23 - 31-03-26).xlsx")
eq_w, eq_m, eq_y = get_averages_fixed(df_eq)
uj_w, uj_m, uj_y = get_averages_fixed(df_uj)

with pd.ExcelWriter("NSE_Turnover_Analysis.xlsx", engine='openpyxl') as writer:
    pd.merge(eq_w, uj_w, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Weekly_Analysis', index=False)
    pd.merge(eq_m, uj_m, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Monthly_Analysis', index=False)
    pd.merge(eq_y, uj_y, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).to_excel(writer, sheet_name='Yearly_Analysis', index=False)
    df_eq[['Date', 'Turnover (Lakhs)']].to_excel(writer, sheet_name='Equitas_Raw', index=False)
    df_uj[['Date', 'Turnover (Lakhs)']].to_excel(writer, sheet_name='Ujjivan_Raw', index=False)

print(f"\nFull Excel report regenerated with intuitive labels.")
