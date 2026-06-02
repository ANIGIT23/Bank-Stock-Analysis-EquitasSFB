import pandas as pd
import numpy as np
import glob
import os

# Define the events we found in the data (Format: YYYY-MM-DD)
EVENTS = {
    'Equitas': [
        {'name': 'Q3FY26 Results', 'date': '2026-01-20'},
        {'name': 'Q2FY26 Results / Major Event', 'date': '2025-10-09'}
    ],
    'Ujjivan': [
        {'name': 'Q3FY26 Results', 'date': '2026-01-23'},
        {'name': 'Q2FY26 Results', 'date': '2025-10-29'}
    ]
}

def analyze_event_window(df, event_date, event_name):
    """Calculates metrics Before, During, and After an event."""
    
    # Find the index of the event date
    try:
        event_idx = df[df['Date'] == event_date].index[0]
    except IndexError:
        return None # Date not found
    
    # Define windows (indices: lower index means older date if sorted chronologically)
    # T-3 to T-1
    before_window = df.iloc[max(0, event_idx-3) : event_idx]
    # T to T+1
    during_window = df.iloc[event_idx : min(len(df), event_idx+2)]
    # T+2 to T+4
    after_window = df.iloc[min(len(df), event_idx+2) : min(len(df), event_idx+5)]
    
    metrics = []
    for window_name, window_df in [('1. Before (T-3 to T-1)', before_window), 
                                   ('2. During (T to T+1)', during_window), 
                                   ('3. After (T+2 to T+4)', after_window)]:
        if window_df.empty:
            continue
            
        metrics.append({
            'Event': event_name,
            'Date': event_date,
            'Phase': window_name,
            'Avg Daily Volume (Shares)': window_df['No.of Shares'].mean(),
            'Avg Daily Trades': window_df['No. of Trades'].mean(),
            'Avg Spread H-L (Volatility)': window_df['Spread High-Low'].mean(),
            'Avg Delivery % (Investment Signal)': window_df['% Deli. Qty to Traded Qty'].mean()
        })
        
    return pd.DataFrame(metrics)

def process_bank_data(file_pattern, bank_name):
    print(f"Processing {bank_name}...")
    files = glob.glob(file_pattern)
    if not files:
        print(f"  -> Could not find CSV file for {bank_name}")
        return pd.DataFrame()
        
    # Read the CSV
    df = pd.read_csv(files[0])
    
    # Clean the Date column and sort chronologically (oldest to newest)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%B-%Y')
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Ensure numeric columns are actually numbers
    numeric_cols = ['No.of Shares', 'No. of Trades', 'Spread High-Low', '% Deli. Qty to Traded Qty']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
    all_results = []
    for event in EVENTS[bank_name]:
        event_date = pd.to_datetime(event['date'])
        result_df = analyze_event_window(df, event_date, event['name'])
        if result_df is not None:
            all_results.append(result_df)
            
    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return pd.DataFrame()

# Main Execution
print("Starting Market Event Analysis...")

# Find files using glob (handles the folders you have)
equitas_pattern = "Equitas/*.csv"
ujjivan_pattern = "Ujjivan/*.csv"

# If running directly in the folder where the files are
if not glob.glob(equitas_pattern):
    equitas_pattern = "*Equitas*.csv"
if not glob.glob(ujjivan_pattern):
    ujjivan_pattern = "*Ujjivan*.csv"

equitas_results = process_bank_data(equitas_pattern, 'Equitas')
ujjivan_results = process_bank_data(ujjivan_pattern, 'Ujjivan')

# Save to Excel
output_file = 'Final_Internship_Report_Data.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    if not equitas_results.empty:
        equitas_results.to_excel(writer, sheet_name='Equitas Analysis', index=False)
    if not ujjivan_results.empty:
        ujjivan_results.to_excel(writer, sheet_name='Ujjivan Analysis', index=False)

print(f"\nAnalysis complete! Results saved to: {output_file}")
