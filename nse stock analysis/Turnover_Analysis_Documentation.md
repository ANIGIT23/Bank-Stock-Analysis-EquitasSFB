# Turnover Analysis Project Reference (2023-2026)

This document summarizes the logic, verification steps, and presentation standards used for the Equitas and Ujjivan turnover analysis across NSE and BSE.

## 1. Core Logic & Formulas

### Data Loading
- **Files handled:** Excel (.xlsx) for NSE and CSV (.csv) for BSE.
- **Column Identification:** Uses fuzzy matching to find columns like "Date", "Turnover", and "Quantity" despite variations in exchange formats (e.g., "Turnover ₹" vs "Total Turnover (Rs.)").

### Conversion to Lakhs
All turnover values are converted from absolute Rupees to Lakhs using the following formula:
`Turnover (Lakhs) = Total Turnover / 100,000`

### Aggregation (Averages)
Averages are calculated using "Resampling" logic:
- **Weekly:** `W-MON` (Averages all trading days in a week starting Monday).
- **Monthly:** `MS` (Month Start - averages all days in that calendar month).
- **Yearly:** `YS` (Year Start - averages all days in that calendar year).

## 2. NSE vs BSE Comparison Insights

### Magnitude (The 10x Rule)
- **NSE:** The "Main Highway." Handles roughly 90% of total trading volume. Peaks reach up to 40,000+ Lakhs.
- **BSE:** The "Service Road." Handles roughly 10% of total volume. Peaks reach up to 4,500+ Lakhs.
- **Why compare?** Synchronized spikes across both exchanges confirm that an event is a "Verified Market Event" and not a data glitch.

### Peak Synchronization
- All major peaks (U1-U6, E1-E5) occur on the **exact same dates** on both exchanges, proving that public news affects the entire market simultaneously.

## 3. Presentation & Charting Standards

### Visual Style
- **Visuals:** 72/28 split layout (72% Graph, 28% Info Box). 32-inch width for maximum clarity.
- **Data Markers:** Every weekly data point is marked with a dot (`marker='.'`).
- **Precision:** Markers sit exactly on the mathematical "tips" of the weekly averages.
- **Staggered Labels:** In cases of near-simultaneous events (e.g., U3 and E3 in Dec 2023), labels are vertically offset to prevent overlap.

## 4. The "IT-Graduate" Logic (Explaining to Non-Finance Users)
Turnover is analogous to **Network Traffic**:
- **Baseline:** Standard trading volume is like "Steady-state background traffic."
- **Inflation (Spike):** A "Viral Event" or "DDoS of orders."
- **Good News (e.g., U2 Merger):** Like a "System Integration Success" – huge traffic as everyone updates their holdings.
- **Bad News (e.g., E5 Profit Drop):** Like a "Major System Bug" – huge traffic as users try to "Uninstall" (Sell) at once.
- **Block Deals (e.g., E3):** Like a "Database Migration" – massive volume moved in bulk between large servers (institutional funds).

## 5. Verification Guide (How to check on your own)

### Step 1: Excel Verification
Match the "tips" of the graph with the **`Weekly_Analysis`** sheet in the respective Excel files. 
- Example: **U2** peak on **2023-10-09** in NSE should show **43,606.74 Lakhs**.

### Step 2: Real-World Verification (Google Search Strings)
Search these exact phrases to find the original news headlines:
- **U2 (Oct 2023):** `Ujjivan SFB NCLT merger approval news October 2023`
- **E3 (Dec 2023):** `Equitas SFB block deals NSE December 2023`
- **E5 (Apr 2025):** `Equitas SFB Q4 2025 net profit results April 2025` (Look for the 80% drop news).

### Step 3: Official Corporate Logs
- Visit **nseindia.com** or **bseindia.com**.
- Search for `EQUITASBNK` or `UJJIVANSFB`.
- Check "Corporate Announcements" for the specific dates to see the original PDFs sent by the bank.

## 6. Labeling Standard
To avoid confusion with future dates, all summaries use the **Start of Period** label:
- **Year 2026** is labeled as `2026-01-01`.
- **March 2026** is labeled as `2026-03-01`.

---
*Last updated on April 9, 2026 for ANI Internship Final Presentation.*
