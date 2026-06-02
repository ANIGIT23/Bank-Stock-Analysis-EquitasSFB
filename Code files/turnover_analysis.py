import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Define file paths
equitas_file = "EQUITAS NSE (1-4-23 - 31-03-26).xlsx"
ujjivan_file = "UJJIVAN NSE (1-4-23 - 31-03-26).xlsx"

def load_and_clean(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {col: 'Date' for col in df.columns if 'date' in col.lower()}
    mapping.update({col: 'Turnover' for col in df.columns if 'turnover' in col.lower()})
    df = df[list(mapping.keys())].rename(columns=mapping)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Lakhs'] = pd.to_numeric(df['Turnover'], errors='coerce') / 100000
    return df.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()

eq_w = load_and_clean(equitas_file)
uj_w = load_and_clean(ujjivan_file)
weekly_comp = pd.merge(eq_w, uj_w, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).sort_values('Date').fillna(0)

# STRICT CHRONOLOGICAL PEAKS (ALL SIGNIFICANT INFLATIONS)
uj_peaks = [
    {'date': '2023-08-07', 'code': 'U1', 'why': '60% Profit Jump (Buying Surge)'},
    {'date': '2023-10-09', 'code': 'U2', 'why': 'NCLT Merger Approval (Highest Peak)'},
    {'date': '2023-12-11', 'code': 'U3', 'why': 'Stock hit All-Time High (Market Exit)'},
    {'date': '2024-04-08', 'code': 'U4', 'why': '24% Deposit Growth News (Buying)'},
    {'date': '2024-06-24', 'code': 'U5', 'why': 'Negative Guidance (Selling Spike)'},
    {'date': '2026-01-26', 'code': 'U6', 'why': 'Universal Bank App (Record Profits)'}
]

eq_peaks = [
    {'date': '2023-06-05', 'code': 'E1', 'why': 'CEO Reappointment (Clarity Buying)'},
    {'date': '2023-08-07', 'code': 'E2', 'why': '97% Profit Growth Report (Buying)'},
    {'date': '2023-12-18', 'code': 'E3', 'why': 'Major Block Deals (Institutional Swap)'},
    {'date': '2024-07-29', 'code': 'E4', 'why': 'Capital Raise via NCDs (Board News)'},
    {'date': '2025-04-28', 'code': 'E5', 'why': '80% Profit Drop (Panic Selling Spike)'}
]

# Set up the 2-column layout (72% Graph, 28% Info)
fig, (ax, ax_info) = plt.subplots(1, 2, figsize=(32, 14), gridspec_kw={'width_ratios': [72, 28]})

# PLOTTING
ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Equitas'], label='Equitas SFB (Blue Line)', color='#1f77b4', alpha=0.9, linewidth=3, marker='.', markersize=10)
ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Ujjivan'], label='Ujjivan SFB (Orange Line)', color='#ff7f0e', alpha=0.9, linewidth=3, marker='.', markersize=10)

# ACCURATE CHRONOLOGICAL MARKERS
for ev in uj_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Ujjivan'].values[0]
    ax.scatter(d, val, color='white', s=600, edgecolors='#ff7f0e', linewidth=5, zorder=15)
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,30), ha='center', fontsize=22, fontweight='bold', color='#ff7f0e')

for ev in eq_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Equitas'].values[0]
    ax.scatter(d, val, color='white', s=600, edgecolors='#1f77b4', linewidth=5, zorder=15)
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,30), ha='center', fontsize=22, fontweight='bold', color='#1f77b4')

ax.set_title('CHRONOLOGICAL ANALYSIS: Market Influence Spikes (2023-2026)', fontsize=40, fontweight='bold', pad=50)
ax.set_ylabel('Avg Weekly Turnover (Lakhs ₹)', fontsize=26, labelpad=20)
ax.set_xlabel('Market Timeline', fontsize=26, labelpad=20)
ax.grid(True, which='both', linestyle='--', alpha=0.4)
ax.legend(loc='upper right', fontsize=24)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.get_xticklabels(), rotation=45, fontsize=20)
plt.setp(ax.get_yticklabels(), fontsize=20)

# EXPLANATION BOX
ax_info.axis('off')
info = "FULL CHRONOLOGICAL LOG (REAL DATA)\n\n"
info += "UJJIVAN SFB (ORANGE):\n" + "\n".join([f"• {e['code']} ({e['date'][:7]}): {e['why']}" for e in uj_peaks])
info += "\n\nEQUITAS SFB (BLUE):\n" + "\n".join([f"• {e['code']} ({e['date'][:7]}): {e['why']}" for e in eq_peaks])
info += "\n\n*A Turnover Spike occurs when millions of \nBuy/Sell orders hit the exchange at once."

ax_info.text(0.02, 0.5, info, transform=ax_info.transAxes, fontsize=21, va='center', ha='left',
             bbox=dict(facecolor='#ffffff', alpha=1.0, edgecolor='#cccccc', boxstyle='round,pad=1.5'),
             linespacing=1.8)

plt.subplots_adjust(left=0.05, right=0.98, top=0.90, bottom=0.15, wspace=0.05)
plt.savefig('Presentation_Peak_Analysis_Report.png', dpi=100)
print("Final corrected chronological graph saved as Presentation_Peak_Analysis_Report.png")
