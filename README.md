NSE Momentum Tracker 📈
A simple and powerful momentum dashboard built using Python and Streamlit. It tracks how many days NSE stocks stay in the top gainers and losers list, and shows which ones exit or enter the list each day.
🌐 Live Demo
Click here to view the app
⚙️ Features
Track multi-day gainer and loser streaks
Four side-by-side sections:
🟢 Active Gainers (streak of 2+ days)
🔴 Active Losers (streak of 2+ days)
🟡 Exited Stocks (dropped out today)
🔵 New Entrants (Day 1 additions)
Shows for each stock:
Today's close price (₹)
Today's % change
Streak days
Total cumulative return
Interactive charts using Plotly
Dark theme, clean UI
Data stored locally using SQLite
🛠️ Technologies Used
Python
Streamlit
Plotly
SQLite
pandas
📦 Setup Instructions
Clone this repository:
git clone https://github.com/your-username/your-repo-name.git
Go to the project folder:
cd your-repo-name
Install the dependencies:
pip install -r requirements.txt
Run the app:
streamlit run app.py
Open http://localhost:8501 in your browser.
🧠 How It Works
Each day, today's top movers are compared with yesterday's:
Present in both days → streak increases
Present only today → new entrant (Day 1)
Present only yesterday → exited, with run duration and net return saved
⚠️ Disclaimer
This project is for educational purposes only and is not investment advice.
📄 License
This project is licensed under the MIT License.