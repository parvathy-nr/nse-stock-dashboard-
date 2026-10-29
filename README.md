🎯 Executive Summary & Quant Logic
Standard financial screeners and stock apps only display single-day top gainers and losers. This tool is built for quantitative traders, momentum specialists, and swing investors who want to track multi-session persistence and momentum churn:
🔥 Multi-Day Gainer Streaks – Equities that stay in the top momentum pool over consecutive trading sessions (T, T+1, T+2, …).
❄️ Multi-Day Drawdown Streaks – Persistent selling pressure and distribution trends across consecutive sessions.
🟡 Churn & Exits – Automatically archives when a multi-day runner drops out of the top pool, recording its total run duration and realized cumulative return.
🔵 Day-1 Entrants – Flags stocks entering the top movers list for the first time, giving early trend-following breakout signals.
🏛️ 4-Zone Side-by-Side Terminal Architecture
The dashboard uses a high-contrast dark theme divided into four side-by-side columns:
┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│  🟢 ACTIVE GAINERS   │   🔴 ACTIVE LOSERS   │   🟡 EXITED STOCKS   │   🔵 NEW ENTRANTS    │
│   (Streak ≥ 2 Days)  │   (Streak ≥ 2 Days)  │ (Dropped Out Today)  │   (Day 1 Additions)  │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ 🔥 TRENT (4 Days)    │ ❄️ IDEA (3 Days)     │ 🚪 BHEL (Exited 3d)  │ ⭐ BEL (Day 1, +6.5%)│
│ 🔥 HAL (3 Days)      │ ❄️ PAYTM (2 Days)    │ 🚪 ZEEL (Exited 2d)  │ ⭐ TCS (Day 1, +5.3%)│
│ 🔥 DIXON (2 Days)    │ ❄️ BERGEPAINT (2 Days)│                     │ ⚠️ SRF (Day 1, -5.5%)│
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
Zone
Column
Metrics & Badges Displayed
Zone 1
🟢 Top Gainers (Active Multi-Day Streaks)
🔥 Streak badge (e.g. 🔥 4 Days), today's close (₹), today's % change, previous day's % change, total cumulative % gain since Day 1 entry.
Zone 2
🔴 Top Losers (Active Multi-Day Streaks)
❄️ Drawdown badge (e.g. ❄️ 3 Days), today's close (₹), today's % change, previous day's % change, total cumulative % loss.
Zone 3
🟡 Exited Stocks (Dropped Out Today)
🚪 Exited badge, total run duration (e.g. Ran for 3 Days), realized net return (%), exit price, entry price.
Zone 4
🔵 New Entrants (Day 1 Additions)
⭐ Day 1 Gainer / ⚠️ Day 1 Loser badge, today's close (₹), today's move (%), daily pool rank (e.g. Rank #1).
🧠 How the Streak Logic Works
Each trading day, the app compares today's top-mover pool with the stored history:
Situation
Result
Stock in today's pool and yesterday's pool
Streak count +1 → stays in Zone 1 / 2 (once streak ≥ 2)
Stock in today's pool, not in yesterday's
Day-1 entrant → Zone 4
Stock in yesterday's pool, not in today's
Exited → archived to Zone 3 with run duration and realized return
Cumulative return is calculated from the entry-day price to the latest close. All state is stored locally in SQLite, so nothing leaves your machine.
🛠️ Tech Stack
Python 3.10+
Streamlit 1.35+ – UI and app server
Plotly – interactive charts
SQLite – local persistence of daily pools, streaks, and exits
pandas – data handling
🚀 Getting Started
Prerequisites
Python 3.10 or newer
pip (or any Python package manager)
Installation
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
Run the app
streamlit run app.py
Then open the local URL Streamlit prints (usually http://localhost:8501).
📁 Project Structure
Adjust to match your actual layout.
.
├── app.py              # Streamlit entry point (4-zone dashboard UI)
├── requirements.txt    # Python dependencies
├── data/               # Local SQLite database (git-ignored)
├── LICENSE
└── README.md
🗺️ Roadmap
[ ] Configurable top-N pool size and minimum streak length
[ ] Separate views for Equities vs. F&O universe
[ ] Streak history charts with Plotly
[ ] CSV / Excel export of exits and streaks
[ ] Sector-wise momentum breakdown
🤝 Contributing
Contributions, issues, and feature requests are welcome.
Fork the repo
Create a feature branch (git checkout -b feature/my-feature)
Commit your changes (git commit -m "Add my feature")
Push the branch (git push origin feature/my-feature)
Open a Pull Request
⚠️ Disclaimer
This project is for educational and research purposes only. It is not investment advice. Trading in equities and derivatives involves substantial risk; do your own research before making any financial decision.
📄 License
Distributed under the MIT License. See LICENSE for details.