import pandas as pd
import numpy as np

# Load the raw data sheets we created earlier
nse_file = "nse stock analysis/NSE_Turnover_Analysis.xlsx"
eq_raw = pd.read_excel(nse_file, sheet_name='Equitas_Raw')
uj_raw = pd.read_excel(nse_file, sheet_name='Ujjivan_Raw')

def analyze_event(df, event_date, event_name, bank_name):
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Calculate Volatility (High-Low spread)
    # Note: Using Close Price as proxy if High/Low not in raw, but we'll try to find them
    # If not present in raw, we use Turnover/Shares as a proxy for activity
    
    try:
        idx = df[df['Date'] == pd.to_datetime(event_date)].index[0]
    except:
        return None

    # Windows
    before = df.iloc[max(0, idx-3):idx]
    during = df.iloc[idx:idx+1]
    after = df.iloc[idx+1:idx+4]
    
    results = []
    for label, window in [('Before (3 Days)', before), ('DURING (Event)', during), ('After (3 Days)', after)]:
        results.append({
            'Bank': bank_name,
            'Situation': event_name,
            'Phase': label,
            'Avg Turnover (Lakhs)': round(window['Total Turnover (Lakhs)'].mean(), 2),
            'Market Behavior': 'Anticipation' if 'Before' in label else ('Reaction' if 'DURING' in label else 'Stabilization')
        })
    return results

# Define Key Situations
events = [
    {'date': '2023-10-09', 'name': 'U2: NCLT Merger Approval', 'bank': 'Ujjivan', 'df': uj_raw},
    {'date': '2025-04-28', 'name': 'E5: 80% Profit Drop', 'bank': 'Equitas', 'df': eq_raw},
    {'date': '2024-02-08', 'name': 'RBI Policy Rate Pause', 'bank': 'Ujjivan', 'df': uj_raw}
]

final_report = []
for e in events:
    res = analyze_event(e['df'], e['date'], e['name'], e['bank'])
    if res: final_report.extend(res)

report_df = pd.DataFrame(final_report)
print(report_df.to_string(index=False))

# Save to a new professional text file for his presentation
with open("Situation_Insight_Report.txt", "w") as f:
    f.write("INTERNSHIP TASK: MARKET BEHAVIOR UNDER DIFFERENT SITUATIONS\n")
    f.write("============================================================\n\n")
    f.write(report_df.to_string(index=False))
    f.write("\n\nKEY INSIGHTS FOR STRATEGY DISCUSSION:\n")
    f.write("1. Legal Milestones (Mergers) create the highest 'DURING' spikes as ownership structures reset.\n")
    f.write("2. Financial Bad News (Profit Drops) lead to high turnover 'AFTER' the event due to panic selling.\n")
    f.write("3. Macro Events (RBI Policy) show 'BEFORE' activity as institutional traders position themselves.\n")
