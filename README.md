# ⚡ NSE Ultimate Momentum & Streak Tracker Dashboard
<div align="center">
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
**An institutional-grade, private, local quantitative web application built with Streamlit (Pure Python).**  
Tracks multi-day persistence streaks, runner dropouts (churn), and fresh breakout entrants across the entire universe of Indian NSE Equities and Derivatives (F&O).
</div>
---
## 🎯 Executive Summary & Quant Logic
Standard financial screeners and stock apps only display single-day top gainers and losers. This tool is designed for quantitative traders, momentum specialists, and swing investors to track **Multi-Session Persistence** and **Momentum Churn**:
1. **🔥 Multi-Day Gainer Streaks**: Identifies equities maintaining their position in the top momentum pool over consecutive trading sessions ($T, T+1, T+2, \dots$).
2. **❄️ Multi-Day Drawdown Streaks**: Tracks persistent selling pressure and distribution trends across consecutive sessions.
3. **🟡 Churn & Exits**: Automatically archives when a multi-day runner drops out of the top pool, recording its total run duration and realized cumulative return.
4. **🔵 Day-1 Entrants**: Flags stocks entering the top movers list for the very first time, giving early trend-following breakout signals.
---
## 🏛️ 4-Zone Side-by-Side Terminal Architecture
The dashboard implements a sleek, high-contrast dark theme divided into 4 clear side-by-side columns:
```
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│  🟢 ACTIVE GAINERS   │   🔴 ACTIVE LOSERS   │   🟡 EXITED STOCKS   │   🔵 NEW ENTRANTS    │
│   (Streak ≥ 2 Days)  │   (Streak ≥ 2 Days)  │ (Dropped Out Today)  │   (Day 1 Additions)  │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ 🔥 TRENT (4 Days)    │ ❄️ IDEA (3 Days)     │ 🚪 BHEL (Exited 3d)  │ ⭐ BEL (Day 1, +6.5%)│
│ 🔥 HAL (3 Days)      │ ❄️ PAYTM (2 Days)    │ 🚪 ZEEL (Exited 2d)  │ ⭐ TCS (Day 1, +5.3%)│
│ 🔥 DIXON (2 Days)    │ ❄️ BERGEPAINT (2 Days)│                      │ ⚠️ SRF (Day 1, -5.5%)│
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```
| Zone | Column | Metrics & Badges Displayed |
| :--- | :--- | :--- |
| **Zone 1** | 🟢 **Top Gainers (Active Multi-Day Streaks)** | 🔥 Streak Days Badge (e.g., `🔥 4 Days`), Today's Close (₹), Today's % Change, Previous Day's % Change, and Total Cumulative % Gain since Day 1 entry. |
| **Zone 2** | 🔴 **Top Losers (Active Multi-Day Streaks)** | ❄️ Drawdown Badge (e.g., `❄️ 3 Days`), Today's Close (₹), Today's % Change, Previous Day's % Change, and Total Cumulative % Loss. |
| **Zone 3** | 🟡 **Exited Stocks (Dropped Out Today)** | 🚪 Exited Badge, Total Run Duration (e.g., `Ran for 3 Days`), Realized Net Return (%), Exit Price, and Entry Price. |
| **Zone 4** | 🔵 **New Entrants (Day 1 Additions)** | ⭐ Day 1 Gainer / ⚠️ Day 1 Loser Badge, Today's Close (₹), Today's Move (%), Daily Pool Rank (`Rank #1`). |