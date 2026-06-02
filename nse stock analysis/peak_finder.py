import pandas as pd

def get_peaks(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    d_col = [c for c in df.columns if 'date' in c.lower()][0]
    t_col = [c for c in df.columns if 'turnover' in c.lower()][0]
    df[d_col] = pd.to_datetime(df[d_col], dayfirst=True)
    df['Lakhs'] = pd.to_numeric(df[t_col], errors='coerce') / 100000
    weekly = df.set_index(d_col).resample('W-MON')['Lakhs'].mean().reset_index()
    return weekly.sort_values('Lakhs', ascending=False).head(10)

print("--- EQUITAS TOP PEAKS ---")
print(get_peaks('EQUITAS NSE (1-4-23 - 31-03-26).xlsx'))

print("\n--- UJJIVAN TOP PEAKS ---")
print(get_peaks('UJJIVAN NSE (1-4-23 - 31-03-26).xlsx'))
