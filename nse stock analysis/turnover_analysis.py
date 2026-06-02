import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# Define file paths
equitas_file = "EQUITAS NSE (1-4-23 - 31-03-26).xlsx"
ujjivan_file = "UJJIVAN NSE (1-4-23 - 31-03-26).xlsx"

def clean_numeric(val):
    if isinstance(val, str):
        val = re.sub(r'[^\d.]', '', val)
    try:
        return float(val)
    except:
        return np.nan

def load_and_clean(file_path):
    print(f"Crafting the uploaded file: {file_path} as per the project working structure.")
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
        
    df.columns = [str(c).strip() for c in df.columns]
    
    # Robust mapping
    mapping = {}
    for col in df.columns:
        low_col = col.lower()
        if 'date' in low_col: mapping[col] = 'Date'
        if any(kw in low_col for kw in ['turnover', 'value']): mapping[col] = 'Turnover'
    
    df = df[list(mapping.keys())].rename(columns=mapping).copy()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Handle commas
    df['Turnover'] = df['Turnover'].apply(clean_numeric)
    df['Lakhs'] = df['Turnover'] / 100000
    
    return df.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()

eq_w = load_and_clean(equitas_file)
uj_w = load_and_clean(ujjivan_file)
weekly_comp = pd.merge(eq_w, uj_w, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).sort_values('Date').fillna(0)

# PEAK EVENTS
uj_peaks = [
    {'date': '2023-08-07', 'code': 'U1', 'why': '60% Profit Jump (Q1 FY24) - Massive Buy Demand.'},
    {'date': '2023-10-09', 'code': 'U2', 'why': 'NCLT Merger Approval - Record Market Activity.'},
    {'date': '2023-12-11', 'code': 'U3', 'why': 'Stock hit All-Time High (₹68) - Institutional Peak.'},
    {'date': '2024-04-08', 'code': 'U4', 'why': 'Business Update: 24% Deposit Growth - Strong Buying.'},
    {'date': '2024-06-24', 'code': 'U5', 'why': 'Negative Spike: Market Sell-off on Lowered Guidance.'},
    {'date': '2026-01-26', 'code': 'U6', 'why': 'Record Q3 Profits & Universal Bank License App.'}
]

eq_peaks = [
    {'date': '2023-06-05', 'code': 'E1', 'why': 'CEO PN Vasudevan Reappointment & Merger Momentum.'},
    {'date': '2023-08-07', 'code': 'E2', 'why': '97% Net Profit Jump (Q1 FY24) - Investor Surge.'},
    {'date': '2023-12-18', 'code': 'E3', 'why': 'Major Institutional Block Deals (Big funds swapping).'},
    {'date': '2024-01-08', 'code': 'E4', 'why': 'Trading Surge ahead of Strong Q3 FY24 Earnings.'},
    {'date': '2024-07-29', 'code': 'E5', 'why': 'Board Approval for Raising Capital via NCD Debt.'},
    {'date': '2025-04-28', 'code': 'E6', 'why': 'Negative Spike: 80% Profit Drop Panic Selling.'}
]

# UPDATED: Increased width to 32 and changed ratio to 72:28 for maximum graph expansion
fig, (ax, ax_info) = plt.subplots(1, 2, figsize=(32, 14), gridspec_kw={'width_ratios': [72, 28]})

# GRAPH PLOTTING (Left side)
ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Equitas'], label='Equitas SFB (Blue Line)', color='#1f77b4', alpha=0.9, linewidth=3, marker='.', markersize=10)
ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Ujjivan'], label='Ujjivan SFB (Orange Line)', color='#ff7f0e', alpha=0.9, linewidth=3, marker='.', markersize=10)

# Precise markers
for ev in uj_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Ujjivan'].values[0]
    ax.scatter(d, val, color='white', s=550, edgecolors='#ff7f0e', linewidth=5, zorder=15)
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,28), ha='center', fontsize=20, fontweight='bold', color='#ff7f0e')

for ev in eq_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Equitas'].values[0]
    ax.scatter(d, val, color='white', s=550, edgecolors='#1f77b4', linewidth=5, zorder=15)
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,28), ha='center', fontsize=20, fontweight='bold', color='#1f77b4')

ax.set_title('COMPREHENSIVE PEAK ANALYSIS: 2023-2026', fontsize=36, fontweight='bold', pad=40)
ax.set_ylabel('Avg Weekly Turnover (Lakhs ₹)', fontsize=24, labelpad=20)
ax.set_xlabel('Market Timeline', fontsize=24, labelpad=20)
ax.grid(True, which='both', linestyle='--', alpha=0.4)
ax.legend(loc='upper right', fontsize=22)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.get_xticklabels(), rotation=45, fontsize=18)
plt.setp(ax.get_yticklabels(), fontsize=18)

# EXPLANATION BOX (Right side)
ax_info.axis('off')
info = "FULL CHRONOLOGICAL INFLATION LOG\n\n"
info += "UJJIVAN SFB (ORANGE):\n" + "\n".join([f"• {e['code']}: {e['why']}" for e in uj_peaks])
info += "\n\nEQUITAS SFB (BLUE):\n" + "\n".join([f"• {e['code']}: {e['why']}" for e in eq_peaks])
info += "\n\n*A 'Spike' means millions of orders hit the \nexchange simultaneously due to major news."

# Kept font large (19) but ensured it fits the narrower column
ax_info.text(0.02, 0.5, info, transform=ax_info.transAxes, fontsize=19, va='center', ha='left',
             bbox=dict(facecolor='#ffffff', alpha=1.0, edgecolor='#cccccc', boxstyle='round,pad=1.5'),
             linespacing=1.7)

plt.subplots_adjust(left=0.05, right=0.98, top=0.90, bottom=0.15, wspace=0.05)
plt.savefig('Comprehensive_Turnover_Market_Analysis.png', dpi=100)
print("Updated expanded graph saved as Comprehensive_Turnover_Market_Analysis.png")
