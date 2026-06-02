# Bank Stock Turnover & Event Analysis Tool

An automated tool to analyze market turnover and liquidity patterns for **Equitas Small Finance Bank** and **Ujjivan Small Finance Bank** (2020-2026).

## 🎯 Project Objective
To analyze how stock market activity changes during critical events (like Q3 result announcements in January). The tool detects turnover spikes and correlates them with historical business milestones.

## 🚀 How to Run

### 1. Prerequisites
Ensure you have Python installed, then install the required libraries:
```powershell
pip install pandas matplotlib openpyxl fastapi uvicorn
```

### 2. Start the Application
You can run the Desktop GUI (recommended) or the Web App:

**Desktop GUI:**
```powershell
python Automated_Market_Report/Simple_Market_App.py
```

**Web App:**
```powershell
python Automated_Market_Report/run_app.py
```

### 3. Usage
- Select **NSE** or **BSE** mode.
- Upload the corresponding bank files from the `NSE & BSE DATA/` folder.
- Click **Generate Report** to see the turnover analysis and clickable event logs.

## 📁 Project Structure
- `Automated_Market_Report/`: Core logic and application interfaces.
- `NSE & BSE DATA/`: Comprehensive dataset for NSE (2020-2026) and BSE (2023-2026).
- `Code files/`: Modular scripts for turnover, volatility, and situational analysis.
- `Reports/`: Pre-generated situational and trade pattern reports.
- `nse stock analysis/`: Statistical peak detection and documentation.

## 🛠 Features
- **Statistical Peak Detection:** Automatically identifies unusual trading volume.
- **Historical Event Mapping:** Links turnover spikes to specific corporate actions.
- **Interactive Reports:** Clickable links to Google News for real-time verification of events.
- **Multi-Exchange Support:** Handles both NSE and BSE data formats.
