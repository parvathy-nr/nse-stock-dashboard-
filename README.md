# ⚡ NSE Ultimate Momentum & Streak Tracker Dashboard

<div align="center">

[![Live Web App](https://img.shields.io/badge/Live_App-Open_in_Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://nse-streak-tracker.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

### 🌐 [👉 Click Here to Launch the Live Web App 👈](https://nse-streak-tracker.streamlit.app/)
*Track active multi-day NSE momentum streaks, runner churn, and new breakouts live on any device.*

</div>

---

## 🌐 Live Web Application

The dashboard is deployed live on **Streamlit Community Cloud** and is freely accessible on web and mobile:

🔗 **Live URL:** [https://nse-streak-tracker.streamlit.app/](https://nse-streak-tracker.streamlit.app/)

- 📱 **Mobile & Desktop Ready:** Works seamlessly on smartphones, tablets, and desktop browsers with zero setup.
- ⚡ **Pre-Seeded Quant Engine:** Pre-loaded with official NSE historical trading sessions and continuous multi-day streaks (e.g. TRENT, HAL, BEL).
- 🎨 **Dark Fintech Terminal UI:** Modern high-contrast dark theme with color-coded streak badges and interactive Plotly charts.

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
