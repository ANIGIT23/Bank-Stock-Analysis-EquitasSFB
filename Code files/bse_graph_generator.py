import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

equitas_bse = "EQUITAS BSE (1-4-23 - 31-03-26).csv"
ujjivan_bse = "UJJIVAN BSE (1-4-23 - 31-03-26).csv"

def load_bse_weekly(file_path):
    df = pd.read_csv(file_path)
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {col: 'Date' for col in df.columns if 'date' in col.lower()}
    mapping.update({col: 'Turnover' for col in df.columns if 'turnover' in col.lower()})
    df = df[list(mapping.keys())].rename(columns=mapping)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.dropna(subset=['Date'])
    df['Lakhs'] = pd.to_numeric(df['Turnover'], errors='coerce') / 100000
    return df.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()

eq_w = load_bse_weekly(equitas_bse)
uj_w = load_bse_weekly(ujjivan_bse)
weekly_comp = pd.merge(eq_w, uj_w, on='Date', how='outer', suffixes=('_Equitas', '_Ujjivan')).sort_values('Date').fillna(0)

uj_peaks = [
    {'date': '2023-08-07', 'code': 'U1', 'why': 'Q1 Profit Jump Surge'},
    {'date': '2023-10-09', 'code': 'U2', 'why': 'NCLT Merger Approval Peak'},
    {'date': '2023-12-11', 'code': 'U3', 'why': 'All-Time High (₹68) Exit'},
    {'date': '2024-04-08', 'code': 'U4', 'why': '24% Deposit Growth Update'},
    {'date': '2024-06-24', 'code': 'U5', 'why': 'Market Guidance Sell-off'},
    {'date': '2026-01-26', 'code': 'U6', 'why': 'Universal Bank App News'}
]

eq_peaks = [
    {'date': '2023-06-05', 'code': 'E1', 'why': 'CEO Reappointment News'},
    {'date': '2023-08-07', 'code': 'E2', 'why': '97% Profit Jump Activity'},
    {'date': '2023-12-18', 'code': 'E3', 'why': 'Major Block Deals'},
    {'date': '2024-07-29', 'code': 'E4', 'why': 'Capital Raising (NCD) News'},
    {'date': '2025-04-28', 'code': 'E5', 'why': '80% Profit Drop Sell-off'}
]

fig, (ax, ax_info) = plt.subplots(1, 2, figsize=(32, 14), gridspec_kw={'width_ratios': [72, 28]})

ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Equitas'], label='Equitas SFB (BSE Blue)', color='#1f77b4', alpha=0.9, linewidth=3, marker='.', markersize=10)
ax.plot(weekly_comp['Date'], weekly_comp['Lakhs_Ujjivan'], label='Ujjivan SFB (BSE Orange)', color='#ff7f0e', alpha=0.9, linewidth=3, marker='.', markersize=10)

# Offset logic to prevent U3/E3 collision
for ev in uj_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Ujjivan'].values[0]
    ax.scatter(d, val, color='white', s=600, edgecolors='#ff7f0e', linewidth=5, zorder=15)
    # Move U3 label slightly higher
    y_off = 45 if ev['code'] == 'U3' else 30
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,y_off), ha='center', fontsize=22, fontweight='bold', color='#ff7f0e')

for ev in eq_peaks:
    d = pd.to_datetime(ev['date'])
    val = weekly_comp.loc[weekly_comp['Date'] == d, 'Lakhs_Equitas'].values[0]
    ax.scatter(d, val, color='white', s=600, edgecolors='#1f77b4', linewidth=5, zorder=15)
    # Move E3 label slightly lower if needed, but here we just shift its partner U3 up
    ax.annotate(ev['code'], (d, val), textcoords="offset points", xytext=(0,30), ha='center', fontsize=22, fontweight='bold', color='#1f77b4')

ax.set_title('BSE CHRONOLOGICAL PEAK ANALYSIS (2023-2026)', fontsize=40, fontweight='bold', pad=50)
ax.set_ylabel('Avg Weekly Turnover (Lakhs ₹)', fontsize=26, labelpad=20)
ax.set_xlabel('BSE Trading Timeline', fontsize=26, labelpad=20)
ax.grid(True, which='both', linestyle='--', alpha=0.4)
ax.legend(loc='upper right', fontsize=24)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.get_xticklabels(), rotation=45, fontsize=20)
plt.setp(ax.get_yticklabels(), fontsize=20)

ax_info.axis('off')
info = "BSE MARKET INFLATION LOG\n\n"
info += "UJJIVAN SFB (ORANGE):\n" + "\n".join([f"• {e['code']}: {e['why']}" for e in uj_peaks])
info += "\n\nEQUITAS SFB (BLUE):\n" + "\n".join([f"• {e['code']}: {e['why']}" for e in eq_peaks])
info += "\n\n*BSE Turnover represents trading volume \nspecifically on the Bombay Stock Exchange."

ax_info.text(0.02, 0.5, info, transform=ax_info.transAxes, fontsize=21, va='center', ha='left',
             bbox=dict(facecolor='#ffffff', alpha=1.0, edgecolor='#cccccc', boxstyle='round,pad=1.5'),
             linespacing=1.8)

plt.subplots_adjust(left=0.05, right=0.98, top=0.90, bottom=0.15, wspace=0.05)
plt.savefig('BSE_Peak_Analysis_Report.png', dpi=100)
print("BSE graph updated with staggered labels to prevent collision.")
