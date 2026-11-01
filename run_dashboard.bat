@echo off
title NSE Momentum Dashboard
cd /d "%~dp0"
echo Starting NSE Momentum & Streak Tracker Dashboard...
start http://localhost:8501
streamlit run app.py --server.headless false
pause
