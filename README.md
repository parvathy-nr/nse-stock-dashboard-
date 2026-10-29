# NSE Momentum Tracker 📈

A simple and powerful momentum dashboard built using Python and Streamlit. It tracks how many days NSE stocks stay in the top gainers and losers list, and shows which ones exit or enter the list each day.

---

## 🌐 Live Demo

[Click here to view the app](https://your-app-link-here)

---

## ⚙️ Features

- Track multi-day gainer and loser streaks
- Four side-by-side sections:
  - 🟢 Active Gainers (streak of 2+ days)
  - 🔴 Active Losers (streak of 2+ days)
  - 🟡 Exited Stocks (dropped out today)
  - 🔵 New Entrants (Day 1 additions)
- Shows for each stock:
  - Today's close price (₹)
  - Today's % change
  - Streak days
  - Total cumulative return
- Interactive charts using Plotly
- Dark theme, clean UI
- Data stored locally using SQLite

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Plotly
- SQLite
- pandas

---

## 📦 Setup Instructions

1. Clone this repository:

   ```bash
   git clone https://github.com/parvathy-nr/nse-stock-dashboard-.git
   ```

2. Go to the project folder:

   ```bash
   cd nse-stock-dashboard-
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

5. Open `http://localhost:8501` in your browser.

---

## 🧠 How It Works

Each day, today's top movers are compared with yesterday's:

- Present in both days → streak increases
- Present only today → new entrant (Day 1)
- Present only yesterday → exited, with run duration and net return saved

---

## ⚠️ Disclaimer

This project is for educational purposes only and is not investment advice.

---

## 📄 License

This project is licensed under the MIT License.