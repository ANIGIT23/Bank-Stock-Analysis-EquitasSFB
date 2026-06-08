import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import re

def clean_numeric(val):
    if isinstance(val, str):
        # Remove commas and other non-numeric characters except decimal point
        val = re.sub(r'[^\d.]', '', val)
    try:
        return float(val)
    except:
        return np.nan

def extract_bank_name(file_path):
    # Extract filename without extension
    base = os.path.basename(file_path).upper()
    # Remove common technical suffixes
    base = base.replace('.XLXS.CSV', '').replace('.XLSX', '').replace('.CSV', '')
    base = base.replace('NSE', '').replace('BSE', '').replace('DATA', '')
    # Strip dates (e.g., 1-4-20 - 31-03-23)
    base = re.sub(r'\(.*?\)', '', base)
    base = re.sub(r'\d+-\d+-\d+', '', base)
    # Final cleanup of special chars and spaces
    name = re.sub(r'[^A-Z ]', '', base).strip()
    # Fallback if too short
    if len(name) < 2: return "Unknown_Bank"
    return name.title()

def robust_read_market_data(file_path):
    print(f"Crafting the uploaded file: {file_path} as per the project working structure.")
    bank_name = extract_bank_name(file_path)
    
    # 1. READ FILE
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        try:
            df = pd.read_csv(file_path)
        except:
            df = pd.read_csv(file_path, encoding='latin1')
    
    df = df.copy()
    raw_cols = [str(c).strip().upper() for c in df.columns]
    
    # DETECT EXCHANGE BEFORE RENAMING
    # NSE specific columns: VWAP, LTP, SERIES
    # BSE specific columns: OPEN PRICE, CLOSE PRICE, LAST PRICE
    is_nse = any(x in raw_cols for x in ['VWAP', 'LTP', 'SERIES'])
    detected_exch = "NSE" if is_nse else "BSE"
    
    # 2. STANDARDIZE COLUMNS
    df.columns = [str(c).strip() for c in df.columns]
    mapping = {}
    for col in df.columns:
        low_col = col.lower()
        if 'date' in low_col: mapping[col] = 'Date'
        if any(kw in low_col for kw in ['turnover', 'value']): 
            if 'Date' not in mapping.get(col, ''):
                mapping[col] = 'Turnover'
        if 'high' in low_col: mapping[col] = 'High'
        if 'low' in low_col: mapping[col] = 'Low'
        if any(kw in low_col for kw in ['trade', 'no. of']): mapping[col] = 'Trades'
    
    found_mapping = {k: v for k, v in mapping.items() if v in ['Date', 'Turnover', 'High', 'Low', 'Trades']}
    df = df[list(found_mapping.keys())].rename(columns=found_mapping)
    
    # 3. ROBUST PARSING
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date')
    df['Turnover'] = df['Turnover'].apply(clean_numeric)
    df['Lakhs'] = df['Turnover'] / 100000
    
    if 'Trades' in df.columns:
        df['Trades'] = df['Trades'].apply(clean_numeric)
    else:
        df['Trades'] = 0
        
    return df, bank_name, detected_exch

def process_market_data(file_path, output_folder):
    df, _, _ = robust_read_market_data(file_path)
    
    # 5. RESAMPLE WEEKLY
    weekly = df.set_index('Date').resample('W-MON').agg({
        'Lakhs': 'mean',
        'Trades': 'mean',
        'High': 'max' if 'High' in df.columns else 'mean',
        'Low': 'min' if 'Low' in df.columns else 'mean'
    }).reset_index()
    
    # 6. PEAK DETECTION (STATISTICAL)
    mean_val = weekly['Lakhs'].mean()
    std_val = weekly['Lakhs'].std()
    peaks = weekly[weekly['Lakhs'] > (mean_val + 2.5 * std_val)]
    
    # 7. GENERATE PROFESSIONAL 72/28 GRAPH
    fig, (ax, ax_info) = plt.subplots(1, 2, figsize=(32, 14), gridspec_kw={'width_ratios': [72, 28]})
    
    ax.plot(weekly['Date'], weekly['Lakhs'], color='#1f77b4', linewidth=3, marker='.', alpha=0.8, label='Turnover History')
    
    event_list = []
    for i, (idx, row) in enumerate(peaks.iterrows()):
        code = f"P{i+1}"
        d_str = row['Date'].strftime('%Y-%m-%d')
        ax.scatter(row['Date'], row['Lakhs'], color='red', s=500, edgecolors='black', zorder=10)
        ax.annotate(code, (row['Date'], row['Lakhs']), xytext=(0,25), textcoords='offset points', ha='center', fontsize=20, fontweight='bold')
        
        search_query = f"https://www.google.com/search?q=Bank+stock+news+{d_str}"
        event_list.append(f"{code} ({d_str}): Turnover Spike detected.\n   Check News: {search_query}")

    ax.set_title('AUTOMATED MARKET PEAK ANALYSIS', fontsize=40, pad=40)
    ax.set_ylabel('Weekly Avg Turnover (Lakhs)', fontsize=24)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.grid(True, alpha=0.3)
    
    ax_info.axis('off')
    info_text = "MARKET INFLATION LOG\n(Auto-Detected)\n\n" + "\n\n".join(event_list)
    ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes, fontsize=18, va='top', bbox=dict(facecolor='white', alpha=0.5))
    
    report_path = os.path.join(output_folder, 'Automated_Report.png')
    plt.savefig(report_path, dpi=100)
    plt.close()
    
    return report_path, peaks
