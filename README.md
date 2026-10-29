🎯 Executive Summary & Quant Logic

Standard financial screeners and stock apps only display single-day top gainers and losers. This tool is designed for quantitative traders, momentum specialists, and swing investors to track Multi-Session Persistence and Momentum Churn:

🔥 Multi-Day Gainer Streaks: Identifies equities maintaining their position in the top momentum pool over consecutive trading sessions (
𝑇
,
𝑇
+
1
,
𝑇
+
2
,
…
T,T+1,T+2,…).
❄️ Multi-Day Drawdown Streaks: Tracks persistent selling pressure and distribution trends across consecutive sessions.
🟡 Churn & Exits: Automatically archives when a multi-day runner drops out of the top pool, recording its total run duration and realized cumulative return.
🔵 Day-1 Entrants: Flags stocks entering the top movers list for the very first time, giving early trend-following breakout signals.

🏛️ 4-Zone Side-by-Side Terminal Architecture

The dashboard implements a sleek, high-contrast dark theme divided into 4 clear side-by-side columns:

┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│  🟢 ACTIVE GAINERS   │   🔴 ACTIVE LOSERS   │   🟡 EXITED STOCKS   │   🔵 NEW ENTRANTS    │
│   (Streak ≥ 2 Days)  │   (Streak ≥ 2 Days)  │ (Dropped Out Today)  │   (Day 1 Additions)  │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ 🔥 TRENT (4 Days)    │ ❄️ IDEA (3 Days)     │ 🚪 BHEL (Exited 3d)  │ ⭐ BEL (Day 1, +6.5%)│
│ 🔥 HAL (3 Days)      │ ❄️ PAYTM (2 Days)    │ 🚪 ZEEL (Exited 2d)  │ ⭐ TCS (Day 1, +5.3%)│
│ 🔥 DIXON (2 Days)    │ ❄️ BERGEPAINT (2 Days)│                      │ ⚠️ SRF (Day 1, -5.5%)│
└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘