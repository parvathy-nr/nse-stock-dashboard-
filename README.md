# ⚡ NSE Ultimate Momentum & Streak Tracker Dashboard

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**An institutional-grade, private, local quantitative web application built with Streamlit (Pure Python).**  
Scans and tracks multi-day persistence streaks, runner dropouts (churn), and fresh breakout entrants across the entire universe of Indian NSE Equities and Derivatives (F&O).

</div>

---

## 🎯 Quant State Machine & Momentum Persistence Engine

Standard screeners only display single-day top gainers. This dashboard solves the institutional trader's core problem: **Multi-Session Momentum Persistence** and **Runner Churn**.

### Exact Day-to-Day Transition Rules:
For any trading session $T$ compared against yesterday $T-1$:
1. **🔥 Streak Continuity ($G_T \cap G_{T-1}$)**:
   - If a stock was in yesterday's Top Gainers with streak $N$ (e.g. 4 days), and repeats in today's Top Gainers:
   - Its streak counter **strictly increments** to $N + 1$ (e.g. 5 days, 6 days, 7 days!).
   - Displayed in **🟢 Zone 1: ACTIVE GAINERS** with badge `🔥 X Days` and net cumulative return from Day 1 entry base.
2. **🚪 Exited Stocks ($G_{T-1} \setminus G_T$)**:
   - If a stock was in yesterday's Top Gainers (with streak $N$), but dropped out today:
   - Displayed in **🟡 Zone 3: EXITED STOCKS** with badge `🚪 Exited Gainer`.
   - Mentions its total run duration (`Ran for N Days`), exit price, and realized cumulative return.
3. **⭐ New Entrants ($G_T \setminus G_{T-1}$)**:
   - Any fresh breakout stock entering today's Top Gainers for the first time:
   - Displayed in **🔵 Zone 4: NEW ENTRANTS** with badge `⭐ Day 1 Gainer` (Day 1 Entry).
4. **❄️ Symmetrical Top Losers**:
   - Multi-day drawdowns increment ($N \rightarrow N + 1$) in **🔴 Zone 2: ACTIVE LOSERS** (`❄️ X Days`).
   - Rebounding losers move to **Zone 3: EXITED STOCKS** (`🚪 Exited Loser`).
   - Fresh breakdowns move to **Zone 4: NEW ENTRANTS** (`⚠️ Day 1 Loser`).

---

## 🏛️ 4-Zone Side-by-Side Terminal Architecture

The dashboard is structured into 4 high-contrast, side-by-side terminal columns:

```
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│  🟢 ACTIVE GAINERS   │   🔴 ACTIVE LOSERS   │   🟡 EXITED STOCKS   │   🔵 NEW ENTRANTS    │
│   (Streak ≥ 2 Days)  │   (Streak ≥ 2 Days)  │ (Dropped Out Today)  │   (Day 1 Additions)  │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ 🔥 TRENT (7 Days)    │ ❄️ IDEA (5 Days)     │ 🚪 BHEL (Exited 3d)  │ ⭐ JSWSTEEL (Day 1)  │
│ 🔥 HAL (5 Days)      │ ❄️ PAYTM (4 Days)    │ 🚪 ZEEL (Exited 2d)  │ ⭐ OFSS (Day 1)      │
│ 🔥 BEL (4 Days)      │ ❄️ INDUSINDBK (2d)   │                      │ ⚠️ MARUTI (Day 1)    │
│ 🔥 DIXON (3 Days)    │ ❄️ MOTHERSON (2d)    │                      │ ⚠️ ANGELONE (Day 1)  │
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

| Zone | Column | Metrics & Badges Displayed |
| :--- | :--- | :--- |
| **Zone 1** | 🟢 **Top Gainers (Active Multi-Day Streaks)** | 🔥 Streak Days Badge (e.g., `🔥 6 Days`), Today's Close (₹), Today's % Change, Previous Day's % Change, and Total Cumulative % Gain since Day 1 entry. |
| **Zone 2** | 🔴 **Top Losers (Active Multi-Day Streaks)** | ❄️ Drawdown Badge (e.g., `❄️ 4 Days`), Today's Close (₹), Today's % Change, Previous Day's % Change, and Total Cumulative % Loss. |
| **Zone 3** | 🟡 **Exited Stocks (Dropped Out Today)** | 🚪 Exited Badge, Total Run Duration (e.g., `Ran for 3 Days`), Realized Net Return (%), Exit Price, and Entry Price. |
| **Zone 4** | 🔵 **New Entrants (Day 1 Additions)** | ⭐ Day 1 Gainer / ⚠️ Day 1 Loser Badge, Today's Close (₹), Today's Move (%), Daily Pool Rank (`Rank #1`). |

---

## 🔬 Interactive Point-In-Time Drilldown

Selecting **"🔍 Drilldown"** on any stock card opens a comprehensive analytical view as of that session:
* **Streak Summary KPI Strip**: Entry Date, Initial Baseline Price, Current Price, Streak Days (as of date), and Net Cumulative Return %.
* **Interactive Plotly Visualizer**:
  * Candlestick & price trajectory chart with baseline entry reference markers.
  * Subplot showing Daily % Change bars (green for up, red for down) and traded volume.
* **Day-by-Day Performance Table**:
  * Full audit: `[ Date | Closing Price (₹) | Daily % Change | Cumulative % from Base | Traded Volume | Standing ]`.

---

## ⚙️ Quant Matching Engine & Database Schema

All data is stored locally in an embedded SQLite database (`market_streaks.db`) with **WAL mode (Write-Ahead Logging)**:

* `symbols_universe`: Master list of 180+ liquid NSE F&O equities with sector mappings.
* `daily_quotes`: Historical OHLCV quotes with daily percentage moves.
* `daily_top_movers`: Daily ranked Top N Gainers and Losers pool.
* `streak_registry`: Active and archived multi-day persistence runs.
* `streak_snapshots`: Session-by-session records for every day of a streak.
* `churn_events`: Log of new entrants and exit events with realized returns.
* `pipeline_audit`: Ingestion history, timestamps, and error telemetry.

---

## 🚀 Quickstart Guide

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Run the Streamlit application:
```bash
streamlit run app.py
```
*On Windows, you can also simply double-click [`run_dashboard.bat`](run_dashboard.bat).*

The dashboard will open automatically in your browser at:
`http://localhost:8501`

---

## 🛡️ License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
