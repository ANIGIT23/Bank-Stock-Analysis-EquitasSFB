import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
from datetime import timedelta
import warnings
import re
from logic import robust_read_market_data

warnings.filterwarnings("ignore")

# THE MASTER SOURCE OF TRUTH: Targeted events for 2020-2026
HISTORICAL_LOG = {
    'Ujjivan': {
        # 2020-2023
        '2020-07-13': 'Q1 Results Prep & COVID Provisioning',
        '2021-07-12': 'Reverse Merger Intent Announcement',
        '2021-08-23': 'CEO Nitin Chugh Resignation Shock',
        '2022-09-12': 'QIP Capital Raise (₹475 Crore)',
        '2022-11-07': 'Q2 Results: Record ₹411 Cr Profit',
        '2022-11-14': 'Brokerage Upgrades & Follow-on Buying',
        '2022-12-19': 'Post-QIP Institutional Block Deals',
        '2023-01-23': 'Q3 Update: 33% Loan Growth Surge',
        # 2023-2026
        '2023-08-07': 'Q1 FY24 Massive Profit Jump',
        '2023-10-02': 'Pre-Result Institutional Accumulation',
        '2023-10-09': 'NCLT Merger Approval - Record Activity',
        '2024-04-08': 'Business Update: 24% Growth Surge',
        '2024-06-24': 'Dividend & Swap Ratio Finalization',
        '2024-07-01': 'Reverse Merger Effective Date',
        '2026-01-26': 'Universal Bank License Application'
    },
    'Equitas': {
        # 2020-2023
        '2020-11-02': 'Stock Market Debut (IPO Listing)',
        '2021-07-12': 'Reverse Merger Intent (RBI Policy)',
        '2022-03-21': 'Formal Amalgamation Scheme Approval',
        '2023-02-06': 'Effective Date of Reverse Merger',
        '2023-02-27': 'Merger Record Date & Suspension',
        '2023-03-06': 'Pre-Listing Capital Transition Phase',
        '2023-03-13': 'Listing Day: New Merger Shares Trade',
        '2023-03-20': 'MSCI/Institutional Index Rebalancing',
        # 2023-2026
        '2023-06-05': 'CEO Reappointment & Momentum',
        '2023-08-07': '97% Net Profit Jump (Q1 FY24)',
        '2023-10-23': 'Q2 FY24: 70% Profit Growth Surge',
        '2023-12-18': 'Major Institutional Block Deals',
        '2024-01-08': 'Q3 Business Update Rally',
        '2024-07-29': 'NCD Capital Raise Approval'
    }
}

def get_unique_event(bank, date, used_events):
    target_d = pd.to_datetime(date)
    best_msg = "Significant Market Activity"
    best_diff = 14 # 2 week window
    bank_log = HISTORICAL_LOG.get(bank, {})
    for l_date, l_msg in bank_log.items():
        diff = abs((pd.to_datetime(l_date) - target_d).days)
        if diff < best_diff and l_msg not in used_events:
            best_diff = diff
            best_msg = l_msg
    used_events.add(best_msg)
    return best_msg

def generate_full_package(data_dict, raw_dfs, exch):
    bank_names = list(data_dict.keys())
    all_dates = pd.concat([df['Date'] for df in data_dict.values()])
    start_str = all_dates.min().strftime('%Y-%m-%d')
    end_str = all_dates.max().strftime('%Y-%m-%d')
    
    excel_name = f"{exch}_Analysis_{start_str}_to_{end_str}.xlsx"
    
    # 1. PEAK REGISTRY (Ensures 100% Match between Excel and Image)
    peak_registry = {}
    for bank in bank_names:
        df_bank = data_dict[bank]
        top_6 = df_bank.sort_values('Lakhs', ascending=False).head(6)['Date'].tolist()
        peak_registry[bank] = top_6

    with pd.ExcelWriter(excel_name, engine='openpyxl') as writer:
        p_data = []
        for bank in bank_names:
            df = raw_dfs[bank].copy()
            res = df.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()
            res.columns = ['Date', f'Turnover (Lakhs)_{bank}']
            
            used_ev = set()
            event_col = []
            for d in res['Date']:
                if d in peak_registry[bank]:
                    msg = get_unique_event(bank, d, used_ev)
                    search_q = f"https://www.google.com/search?q={bank}+SFB+news+on+{d.date()}"
                    event_col.append(f'=HYPERLINK("{search_q}", "{msg}")')
                else:
                    event_col.append("")
            
            res[f'Historical Event_{bank}'] = event_col
            p_data.append(res)
        
        merged_weekly = p_data[0]
        for next_p in p_data[1:]: merged_weekly = pd.merge(merged_weekly, next_p, on='Date', how='outer')
        merged_weekly.sort_values('Date').fillna(0).to_excel(writer, sheet_name='Weekly_Analysis', index=False)
        for bank in bank_names:
            raw_clean = raw_dfs[bank][['Date', 'Lakhs']].rename(columns={'Lakhs':'Turnover (Lakhs)'})
            raw_clean.to_excel(writer, sheet_name=f'{bank}_Raw', index=False)

    # 2. SYNCED PROFESSIONAL PLOT
    fig, (ax, ax_info) = plt.subplots(1, 2, figsize=(46, 20), gridspec_kw={'width_ratios': [75, 25]})
    colors = ['#1f77b4', '#ff7f0e']
    line_styles = ['-', '--'] 
    log_entries, links, date_occupancy = [], [], {}
    global_max = max([df['Lakhs'].max() for df in data_dict.values()])

    for idx, bank in enumerate(bank_names):
        df = data_dict[bank]
        color = colors[idx % 2]
        style = line_styles[idx % 2]
        ax.plot(df['Date'], df['Lakhs'], color=color, linestyle=style, linewidth=5.5, marker='.', markersize=7, label=f"{bank} SFB", alpha=0.85, zorder=10)
        
        top_dates = peak_registry[bank]
        peaks = df[df['Date'].isin(top_dates)].sort_values('Date')
        used_ev_plot = set()
        
        prefix = bank[0].upper()
        for i, (_, row) in enumerate(peaks.iterrows()):
            d = row['Date']
            ds = d.strftime('%Y-%m-%d')
            code = f"{prefix}{i+1}"
            reason = get_unique_event(bank, d, used_ev_plot)
            
            y_offset = 50
            if ds in date_occupancy: y_offset = date_occupancy[ds] + 80
            date_occupancy[ds] = y_offset
            
            ax.scatter(d, row['Lakhs'], facecolor='none', edgecolor=color, s=650, lw=4, zorder=100)
            ax.annotate(code, (d, row['Lakhs']), xytext=(0, y_offset), textcoords='offset points', ha='center', fontsize=26, fontweight='bold', color=color)
            links.append({'code': code, 'link': f"https://www.google.com/search?q={bank}+SFB+news+on+{ds}"})
            log_entries.append(f"• {code}: {reason} ({ds})")

    ax.set_ylim(0, global_max * 1.5) # Forced headroom for neatness
    ax.set_title(f'MARKET TURNOVER & LIQUIDITY ANALYSIS', fontsize=58, fontweight='bold', pad=100)
    ax.set_ylabel('Weekly Avg Turnover (Lakhs ₹)', fontsize=38, labelpad=30)
    ax.grid(True, alpha=0.2)
    # Legend below to ensure zero collision
    ax.legend(fontsize=32, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=True, shadow=True)

    ax_info.axis('off')
    log_title = f"HISTORICAL EVENT LOG\n" + "-"*20 + "\n\n"
    log_body = "\n\n".join(log_entries)
    ax_info.text(0.02, 0.98, log_title + log_body, transform=ax_info.transAxes, fontsize=20, va='top', bbox=dict(boxstyle='round,pad=1.5', facecolor='#ffffff', edgecolor='#dddddd', alpha=1.0), linespacing=1.7, wrap=True)
    
    img_name = f"{exch}_Analysis_{start_str}_to_{end_str}.png"
    plt.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.20, wspace=0.1)
    plt.savefig(img_name, dpi=100)
    plt.close(fig)
    return img_name, excel_name, links

class MarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Market Automator v7.0")
        self.root.geometry("950x900")
        self.exch = tk.StringVar(value="NSE")
        self.data_map, self.raw_map, self.paths = {}, {}, []
        tk.Label(root, text="Bank Stock Analysis Automator", font=("Arial", 32, "bold"), fg='#2c3e50').pack(pady=45)
        f_ex = tk.Frame(root); f_ex.pack(pady=10)
        tk.Radiobutton(f_ex, text="NSE Data", variable=self.exch, value="NSE", font=("Arial", 16)).pack(side=tk.LEFT, padx=65)
        tk.Radiobutton(f_ex, text="BSE Data", variable=self.exch, value="BSE", font=("Arial", 16)).pack(side=tk.LEFT, padx=65)
        self.b1 = tk.Button(root, text="📁 Upload Bank 1 File", command=lambda: self.up(0), bg='#3498db', fg='white', width=45, height=2, font=("Arial", 13, "bold"))
        self.b1.pack(pady=20)
        self.b2 = tk.Button(root, text="📁 Upload Bank 2 File", command=lambda: self.up(1), bg='#3498db', fg='white', width=45, height=2, font=("Arial", 13, "bold"))
        self.b2.pack(pady=20)
        self.run_btn = tk.Button(root, text="🚀 Generate Clickable Professional Report", command=self.finish, bg='#27ae60', fg='white', width=50, height=2, state='disabled', font=("Arial", 15, "bold"))
        self.run_btn.pack(pady=55)
        self.st = tk.Label(root, text="Ready.", font=("Arial", 12), fg='#7f8c8d')
        self.st.pack()
        self.l_frame = tk.Frame(root); self.l_frame.pack(pady=20)

    def up(self, idx):
        p = filedialog.askopenfilename()
        if not p: return
        try:
            df, bank, detected_exch = robust_read_market_data(p)
            selected = self.exch.get()
            if selected != detected_exch:
                if not messagebox.askyesno("Check", f"File looks like {detected_exch}. Proceed anyway?"): return
            if bank in self.data_map:
                messagebox.showerror("Error", f"Bank '{bank}' is already loaded.")
                return
            self.paths.append(p)
            self.raw_map[bank] = df.copy()
            self.data_map[bank] = df.set_index('Date').resample('W-MON')['Lakhs'].mean().reset_index()
            btn = self.b1 if idx == 0 else self.b2
            btn.config(text=f"✅ {bank} Loaded", bg='#95a5a6', state='disabled')
            self.st.config(text=f"Loaded {bank}: {df['Date'].min().date()} to {df['Date'].max().date()}", fg='#27ae60')
            if len(self.data_map) >= 2: self.run_btn.config(state='normal')
        except Exception as e: messagebox.showerror("Validation Error", str(e))

    def finish(self):
        try:
            self.st.config(text="Building Final Report...", fg='#e67e22')
            self.root.update_idletasks()
            img, excel, links = generate_full_package(self.data_map, self.raw_map, self.exch.get())
            self.st.config(text=f"DONE! Saved to folder.", fg='#27ae60')
            for w in self.l_frame.winfo_children(): w.destroy()
            tk.Label(self.l_frame, text="Verify Events via Google News:", font=("Arial", 12, "bold")).pack()
            f = tk.Frame(self.l_frame); f.pack()
            for i, p in enumerate(links):
                if i % 10 == 0: f = tk.Frame(self.l_frame); f.pack()
                tk.Button(f, text=p['code'], command=lambda l=p['link']: webbrowser.open(l), width=5, bg='#ecf0f1').pack(side=tk.LEFT, padx=2)
            messagebox.showinfo("Success", f"Professional Sync Complete!\n\n1. Image: {img}\n2. Excel: {excel}")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MarketApp(root)
    root.mainloop()
