import pandas as pd

def load_weekly(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {}
    for col in df.columns:
        if 'date' in col.lower(): mapping[col] = 'Date'
        if 'turnover' in col.lower(): mapping[col] = 'Total Turnover'
    df = df[list(mapping.keys())].rename(columns=mapping)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Turnover (Lakhs)'] = pd.to_numeric(df['Total Turnover'], errors='coerce') / 100000
    # Match the resampling used in the graph
    return df.set_index('Date').resample('W-MON')['Turnover (Lakhs)'].mean().reset_index()

eq_w = load_weekly("EQUITAS NSE (1-4-23 - 31-03-26).xlsx")
uj_w = load_weekly("UJJIVAN NSE (1-4-23 - 31-03-26).xlsx")

print("--- ACTUAL PEAKS IN WEEKLY DATA (EQUITAS) ---")
print(eq_w.sort_values('Turnover (Lakhs)', ascending=False).head(5))

print("\n--- ACTUAL PEAKS IN WEEKLY DATA (UJJIVAN) ---")
print(uj_w.sort_values('Turnover (Lakhs)', ascending=False).head(5))
