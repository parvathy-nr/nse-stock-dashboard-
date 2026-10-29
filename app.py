"""
================================================================================
NSE Ultimate Momentum & Streak Tracker Dashboard
Framework: Streamlit (Pure Python) | Database: Embedded SQLite (market_streaks.db)
Author: Quant Financial Engineer & Streamlit Developer
================================================================================
Core Scope:
- Scans the entire universe of Indian NSE Equity and F&O (Futures & Options) scrips at EOD.
- Computes daily price % changes, ranks Top Gainers & Losers.
- Tracks MULTI-DAY PERSISTENCE (Streaks) and CHURN (New Entrants & Exited Stocks).
- 4-Zone Side-by-Side Layout: Active Gainers, Active Losers, Exited Stocks, Day-1 Entrants.
- Interactive Drill-Down with Streak Summary, Plotly Charts, and Day-by-Day Performance.
- Background post-market automated EOD scheduling.
================================================================================
"""

import os
import io
import time
import json
import sqlite3
import zipfile
import threading
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# -----------------------------------------------------------------------------
# 1. STREAMLIT CONFIGURATION & CUSTOM DARK THEME CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NSE Momentum & Streak Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* Main Dark Theme Styling */
.stApp {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Header & Banner */
.main-header {
    background: linear-gradient(135deg, #131b2e 0%, #1e293b 100%);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
.main-header h1 {
    color: #f8fafc;
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 6px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}
.main-header p {
    color: #94a3b8;
    font-size: 14px;
    margin: 0;
}

/* KPI Strip */
.kpi-container {
    display: flex;
    gap: 12px;
    margin-top: 16px;
    flex-wrap: wrap;
}
.kpi-chip {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.kpi-chip-label {
    font-size: 12px;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.kpi-chip-val {
    font-size: 15px;
    font-weight: 700;
    color: #f1f5f9;
    font-family: "SF Mono", "Fira Code", monospace;
}

/* 4-Zone Column Headers */
.zone-header {
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 14px;
    font-weight: 700;
    font-size: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.zone-gainer {
    background: linear-gradient(90deg, rgba(16, 185, 129, 0.18) 0%, rgba(16, 185, 129, 0.05) 100%);
    border-left: 4px solid #10b981;
    border-top: 1px solid rgba(16, 185, 129, 0.2);
    border-right: 1px solid rgba(16, 185, 129, 0.1);
    border-bottom: 1px solid rgba(16, 185, 129, 0.1);
    color: #34d399;
}
.zone-loser {
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.18) 0%, rgba(239, 68, 68, 0.05) 100%);
    border-left: 4px solid #ef4444;
    border-top: 1px solid rgba(239, 68, 68, 0.2);
    border-right: 1px solid rgba(239, 68, 68, 0.1);
    border-bottom: 1px solid rgba(239, 68, 68, 0.1);
    color: #f87171;
}
.zone-exit {
    background: linear-gradient(90deg, rgba(245, 158, 11, 0.18) 0%, rgba(245, 158, 11, 0.05) 100%);
    border-left: 4px solid #f59e0b;
    border-top: 1px solid rgba(245, 158, 11, 0.2);
    border-right: 1px solid rgba(245, 158, 11, 0.1);
    border-bottom: 1px solid rgba(245, 158, 11, 0.1);
    color: #fbbf24;
}
.zone-entrant {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.18) 0%, rgba(99, 102, 241, 0.05) 100%);
    border-left: 4px solid #6366f1;
    border-top: 1px solid rgba(99, 102, 241, 0.2);
    border-right: 1px solid rgba(99, 102, 241, 0.1);
    border-bottom: 1px solid rgba(99, 102, 241, 0.1);
    color: #818cf8;
}

/* Card Styling */
.stock-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
}
.stock-card:hover {
    border-color: #374151;
    background: #151f32;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
}
.stock-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}
.stock-symbol {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.3px;
}
.stock-name {
    font-size: 11px;
    color: #64748b;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 130px;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-fire {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
}
.badge-frost {
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.4);
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
}
.badge-exit-gainer {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}
.badge-exit-loser {
    background: rgba(148, 163, 184, 0.15);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.3);
}
.badge-entrant-gainer {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}
.badge-entrant-loser {
    background: rgba(244, 63, 94, 0.15);
    color: #fb7185;
    border: 1px solid rgba(244, 63, 94, 0.4);
}

/* Card Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.metric-item {
    display: flex;
    flex-direction: column;
}
.metric-label {
    font-size: 10px;
    color: #94a3b8;
    text-transform: uppercase;
}
.metric-val {
    font-size: 13px;
    font-weight: 600;
    font-family: "SF Mono", "Fira Code", monospace;
    color: #e2e8f0;
}
.metric-val.green {
    color: #10b981;
}
.metric-val.red {
    color: #f43f5e;
}

/* Inspect button overrides inside cards */
div[data-testid="stButton"] button {
    background-color: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.15s ease;
}
div[data-testid="stButton"] button:hover {
    background-color: #334155;
    color: #ffffff;
    border-color: #475569;
}

/* Drill-Down Panel */
.drilldown-container {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-top: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

/* Empty State Placeholder */
.empty-zone {
    background: rgba(17, 24, 39, 0.4);
    border: 1px dashed #374151;
    border-radius: 8px;
    padding: 24px 16px;
    text-align: center;
    color: #64748b;
    font-size: 13px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. LOCAL SQLITE DATABASE INITIALIZATION (`market_streaks.db`)
# -----------------------------------------------------------------------------
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "market_streaks.db")

def get_db_connection() -> sqlite3.Connection:
    """Provides a thread-safe connection with WAL mode enabled."""
    conn = sqlite3.connect(DB_FILE, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables for universe, quotes, streaks, churn, and scheduler."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Stocks Universe Master
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbols_universe (
            symbol TEXT PRIMARY KEY,
            company_name TEXT,
            sector TEXT,
            is_fno INTEGER DEFAULT 1,
            is_nifty50 INTEGER DEFAULT 0,
            base_price REAL DEFAULT 1000.0
        );
        """)

        # 2. Daily Price Quotes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_quotes (
            trade_date TEXT,
            symbol TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            prev_close REAL,
            pct_change REAL,
            volume INTEGER,
            PRIMARY KEY (trade_date, symbol)
        );
        """)

        # 3. Daily Top Movers Pool
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_top_movers (
            trade_date TEXT,
            category TEXT,       -- 'GAINER' or 'LOSER'
            rank INTEGER,
            symbol TEXT,
            pct_change REAL,
            close REAL,
            prev_close REAL,
            PRIMARY KEY (trade_date, category, rank)
        );
        """)

        # 4. Multi-Day Streak Registry
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS streak_registry (
            streak_id TEXT PRIMARY KEY,
            symbol TEXT,
            category TEXT,       -- 'GAINER' or 'LOSER'
            start_date TEXT,
            last_date TEXT,
            streak_days INTEGER,
            entry_price REAL,
            last_price REAL,
            cum_return_pct REAL,
            status TEXT          -- 'ACTIVE' or 'EXITED'
        );
        """)

        # 5. Day-by-Day Streak Snapshots
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS streak_snapshots (
            streak_id TEXT,
            trade_date TEXT,
            day_index INTEGER,
            symbol TEXT,
            close REAL,
            daily_pct REAL,
            cum_pct REAL,
            rank_on_day INTEGER,
            PRIMARY KEY (streak_id, trade_date)
        );
        """)

        # 6. Churn Events (Exits & New Entrants)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS churn_events (
            trade_date TEXT,
            symbol TEXT,
            event_type TEXT,     -- 'NEW_ENTRANT' or 'EXITED'
            category TEXT,       -- 'GAINER' or 'LOSER'
            streak_days INTEGER,
            return_pct REAL,
            exit_price REAL,
            entry_price REAL,
            PRIMARY KEY (trade_date, symbol, event_type)
        );
        """)

        # 7. Audit & Pipeline Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_name TEXT,
            status TEXT,
            details TEXT,
            records_count INTEGER DEFAULT 0
        );
        """)
        
        conn.commit()

init_db()

# -----------------------------------------------------------------------------
# 3. COMPREHENSIVE NSE UNIVERSE (F&O & NIFTY 50 EQUITIES)
# -----------------------------------------------------------------------------
DEFAULT_NSE_FNO_UNIVERSE = [
    # Symbol, Company Name, Sector, is_nifty50, seed_price
    ("RELIANCE", "Reliance Industries Ltd.", "Oil & Gas", 1, 2740.0),
    ("TCS", "Tata Consultancy Services Ltd.", "IT Services", 1, 3920.0),
    ("HDFCBANK", "HDFC Bank Ltd.", "Banking", 1, 1680.0),
    ("INFY", "Infosys Ltd.", "IT Services", 1, 1850.0),
    ("ICICIBANK", "ICICI Bank Ltd.", "Banking", 1, 1220.0),
    ("BHARTIARTL", "Bharti Airtel Ltd.", "Telecom", 1, 1640.0),
    ("SBIN", "State Bank of India", "Banking", 1, 795.0),
    ("LT", "Larsen & Toubro Ltd.", "Infrastructure", 1, 3580.0),
    ("BAJFINANCE", "Bajaj Finance Ltd.", "NBFC", 1, 6950.0),
    ("MARUTI", "Maruti Suzuki India Ltd.", "Automobile", 1, 11800.0),
    ("TATAMOTORS", "Tata Motors Ltd.", "Automobile", 1, 910.0),
    ("AXISBANK", "Axis Bank Ltd.", "Banking", 1, 1180.0),
    ("KOTAKBANK", "Kotak Mahindra Bank Ltd.", "Banking", 1, 1780.0),
    ("SUNPHARMA", "Sun Pharmaceutical Inds.", "Pharma", 1, 1890.0),
    ("TITAN", "Titan Company Ltd.", "Consumer Durables", 1, 3350.0),
    ("ITC", "ITC Ltd.", "FMCG", 1, 485.0),
    ("ADANIENT", "Adani Enterprises Ltd.", "Metals & Mining", 1, 2980.0),
    ("ADANIPORTS", "Adani Ports and SEZ Ltd.", "Logistics", 1, 1370.0),
    ("COALINDIA", "Coal India Ltd.", "Mining", 1, 460.0),
    ("NTPC", "NTPC Ltd.", "Power", 1, 415.0),
    ("ONGC", "Oil & Natural Gas Corp.", "Oil & Gas", 1, 285.0),
    ("POWERGRID", "Power Grid Corp. of India", "Power", 1, 330.0),
    ("TATASTEEL", "Tata Steel Ltd.", "Metals", 1, 148.0),
    ("JSWSTEEL", "JSW Steel Ltd.", "Metals", 1, 960.0),
    ("HINDALCO", "Hindalco Industries Ltd.", "Metals", 1, 680.0),
    ("VEDL", "Vedanta Ltd.", "Metals", 0, 485.0),
    ("BHEL", "Bharat Heavy Electricals Ltd.", "Capital Goods", 0, 245.0),
    ("HAL", "Hindustan Aeronautics Ltd.", "Defense", 0, 4350.0),
    ("BEL", "Bharat Electronics Ltd.", "Defense", 0, 295.0),
    ("ZOMATO", "Zomato Ltd.", "Consumer Tech", 0, 260.0),
    ("TRENT", "Trent Ltd.", "Retail", 0, 7450.0),
    ("DIXON", "Dixon Technologies Ltd.", "Consumer Durables", 0, 13200.0),
    ("POLYCAB", "Polycab India Ltd.", "Cables & Wires", 0, 6850.0),
    ("PERSISTENT", "Persistent Systems Ltd.", "IT Services", 0, 5350.0),
    ("COFORGE", "Coforge Ltd.", "IT Services", 0, 7800.0),
    ("TECHM", "Tech Mahindra Ltd.", "IT Services", 1, 1680.0),
    ("WIPRO", "Wipro Ltd.", "IT Services", 1, 550.0),
    ("HCLTECH", "HCL Technologies Ltd.", "IT Services", 1, 1840.0),
    ("HEROMOTOCO", "Hero MotoCorp Ltd.", "Automobile", 1, 4920.0),
    ("BAJAJ-AUTO", "Bajaj Auto Ltd.", "Automobile", 1, 9850.0),
    ("TVSMOTOR", "TVS Motor Company Ltd.", "Automobile", 0, 2450.0),
    ("EICHERMOT", "Eicher Motors Ltd.", "Automobile", 1, 4780.0),
    ("DRREDDY", "Dr. Reddy's Laboratories", "Pharma", 1, 6580.0),
    ("CIPLA", "Cipla Ltd.", "Pharma", 1, 1530.0),
    ("APOLLOHOSP", "Apollo Hospitals Enterprise", "Healthcare", 1, 7150.0),
    ("DIVISLAB", "Divi's Laboratories Ltd.", "Pharma", 0, 5820.0),
    ("LUPIN", "Lupin Ltd.", "Pharma", 0, 2180.0),
    ("BIOCON", "Biocon Ltd.", "Biopharma", 0, 340.0),
    ("AUROPHARMA", "Aurobindo Pharma Ltd.", "Pharma", 0, 1480.0),
    ("DLF", "DLF Ltd.", "Real Estate", 0, 830.0),
    ("GODREJPROP", "Godrej Properties Ltd.", "Real Estate", 0, 2850.0),
    ("OBEROIRLTY", "Oberoi Realty Ltd.", "Real Estate", 0, 1920.0),
    ("PNB", "Punjab National Bank", "Banking", 0, 102.0),
    ("BANKBARODA", "Bank of Baroda", "Banking", 0, 245.0),
    ("CANBK", "Canara Bank", "Banking", 0, 101.0),
    ("FEDERALBNK", "Federal Bank Ltd.", "Banking", 0, 198.0),
    ("INDUSINDBK", "IndusInd Bank Ltd.", "Banking", 1, 1260.0),
    ("IDFCFIRSTB", "IDFC First Bank Ltd.", "Banking", 0, 71.0),
    ("CHOLAFIN", "Cholamandalam Investment", "NBFC", 0, 1420.0),
    ("SHRIRAMFIN", "Shriram Finance Ltd.", "NBFC", 1, 3180.0),
    ("MUTHOOTFIN", "Muthoot Finance Ltd.", "NBFC", 0, 1950.0),
    ("PFC", "Power Finance Corporation", "NBFC", 0, 460.0),
    ("RECLTD", "REC Ltd.", "NBFC", 0, 520.0),
    ("SBILIFE", "SBI Life Insurance Co.", "Insurance", 1, 1680.0),
    ("HDFCLIFE", "HDFC Life Insurance Co.", "Insurance", 1, 720.0),
    ("ICICIPRULI", "ICICI Prudential Life Ins.", "Insurance", 0, 740.0),
    ("SIEMENS", "Siemens Ltd.", "Capital Goods", 0, 7100.0),
    ("ABB", "ABB India Ltd.", "Capital Goods", 0, 7850.0),
    ("CUMMINSIND", "Cummins India Ltd.", "Capital Goods", 0, 3680.0),
    ("BSOFT", "Birlasoft Ltd.", "IT Services", 0, 580.0),
    ("LTTS", "L&T Technology Services", "IT Services", 0, 5150.0),
    ("LTIM", "LTIMindtree Ltd.", "IT Services", 0, 5850.0),
    ("MPHASIS", "Mphasis Ltd.", "IT Services", 0, 2920.0),
    ("KPITTECH", "KPIT Technologies Ltd.", "IT Services", 0, 1620.0),
    ("TATACHEM", "Tata Chemicals Ltd.", "Chemicals", 0, 1040.0),
    ("DEEPAKNTR", "Deepak Nitrite Ltd.", "Chemicals", 0, 2680.0),
    ("PIIND", "PI Industries Ltd.", "Agrochem", 0, 4350.0),
    ("SRF", "SRF Ltd.", "Chemicals", 0, 2240.0),
    ("PIDILITIND", "Pidilite Industries Ltd.", "Chemicals", 0, 3120.0),
    ("ASIANPAINT", "Asian Paints Ltd.", "Paints", 1, 2840.0),
    ("BERGEPAINT", "Berger Paints India Ltd.", "Paints", 0, 510.0),
    ("HINDUNILVR", "Hindustan Unilever Ltd.", "FMCG", 1, 2580.0),
    ("NESTLEIND", "Nestle India Ltd.", "FMCG", 1, 2350.0),
    ("BRITANNIA", "Britannia Industries Ltd.", "FMCG", 1, 5650.0),
    ("DABUR", "Dabur India Ltd.", "FMCG", 0, 530.0),
    ("MARICO", "Marico Ltd.", "FMCG", 0, 640.0),
    ("GODREJCP", "Godrej Consumer Products", "FMCG", 0, 1280.0),
    ("TATACONSUM", "Tata Consumer Products", "FMCG", 1, 1080.0),
    ("AMBUJACEM", "Ambuja Cements Ltd.", "Cement", 0, 560.0),
    ("ACC", "ACC Ltd.", "Cement", 0, 2320.0),
    ("ULTRACEMCO", "UltraTech Cement Ltd.", "Cement", 1, 11200.0),
    ("SHREECEM", "Shree Cement Ltd.", "Cement", 0, 25400.0),
    ("GRASIM", "Grasim Industries Ltd.", "Cement & Fibres", 1, 2650.0),
    ("JINDALSTEL", "Jindal Steel & Power Ltd.", "Metals", 0, 930.0),
    ("SAIL", "Steel Authority of India", "Metals", 0, 122.0),
    ("NATIONALUM", "National Aluminium Co.", "Metals", 0, 215.0),
    ("NMDC", "NMDC Ltd.", "Mining", 0, 228.0),
    ("IOC", "Indian Oil Corporation", "Oil & Gas", 0, 142.0),
    ("BPCL", "Bharat Petroleum Corp.", "Oil & Gas", 1, 315.0),
    ("GAIL", "GAIL (India) Ltd.", "Utilities", 0, 195.0),
    ("PETRONET", "Petronet LNG Ltd.", "Oil & Gas", 0, 310.0),
    ("HINDPETRO", "Hindustan Petroleum Corp.", "Oil & Gas", 0, 345.0),
    ("OIL", "Oil India Ltd.", "Oil & Gas", 0, 510.0),
    ("IGL", "Indraprastha Gas Ltd.", "Utilities", 0, 385.0),
    ("MGL", "Mahanagar Gas Ltd.", "Utilities", 0, 1680.0),
    ("GUJGASLTD", "Gujarat Gas Ltd.", "Utilities", 0, 520.0),
    ("EXIDEIND", "Exide Industries Ltd.", "Auto Ancillary", 0, 460.0),
    ("AMARAJABAT", "Amara Raja Energy & Mobility", "Auto Ancillary", 0, 1340.0),
    ("MOTHERSON", "Samvardhana Motherson Int.", "Auto Ancillary", 0, 172.0),
    ("BHARATFORG", "Bharat Forge Ltd.", "Auto Ancillary", 0, 1380.0),
    ("BOSCHLTD", "Bosch Ltd.", "Auto Ancillary", 0, 34500.0),
    ("BALKRISIND", "Balkrishna Industries Ltd.", "Tyres", 0, 2820.0),
    ("MRF", "MRF Ltd.", "Tyres", 0, 138000.0),
    ("APOLLOTYRE", "Apollo Tyres Ltd.", "Tyres", 0, 510.0),
    ("ESCORTS", "Escorts Kubota Ltd.", "Agri Machinery", 0, 3680.0),
    ("VOLTAS", "Voltas Ltd.", "Consumer Durables", 0, 1780.0),
    ("HAVELLS", "Havells India Ltd.", "Consumer Durables", 0, 1720.0),
    ("CROMPTON", "Crompton Greaves Cons.", "Consumer Durables", 0, 410.0),
    ("BLUESTARCO", "Blue Star Ltd.", "Consumer Durables", 0, 1750.0),
    ("METROPOLIS", "Metropolis Healthcare", "Diagnostics", 0, 2150.0),
    ("LALPATHLAB", "Dr. Lal PathLabs Ltd.", "Diagnostics", 0, 3180.0),
    ("MAXHEALTH", "Max Healthcare Institute", "Hospitals", 0, 980.0),
    ("SYNGENE", "Syngene International", "Research", 0, 840.0),
    ("TORNTPHARM", "Torrent Pharmaceuticals", "Pharma", 0, 3280.0),
    ("ALKEM", "Alkem Laboratories Ltd.", "Pharma", 0, 5450.0),
    ("GLENMARK", "Glenmark Pharmaceuticals", "Pharma", 0, 1680.0),
    ("IPCLAB", "IPCA Laboratories Ltd.", "Pharm
"Pharma", 0, 1540.0),
    ("GRANULES", "Granules India Ltd.", "Pharma", 0, 560.0),
    ("MCX", "Multi Commodity Exchange", "Exchange", 0, 5850.0),
    ("BSE", "BSE Ltd.", "Exchange", 0, 4650.0),
    ("CDSL", "Central Depository Services", "Capital Markets", 0, 1540.0),
    ("CAMS", "Computer Age Mgmt Services", "Capital Markets", 0, 4250.0),
    ("IEX", "Indian Energy Exchange", "Exchange", 0, 185.0),
    ("IRCTC", "Indian Railway Catering", "Travel", 0, 840.0),
    ("INDIGO", "InterGlobe Aviation Ltd.", "Aviation", 0, 4280.0),
    ("JUBLFOOD", "Jubilant FoodWorks Ltd.", "Restaurants", 0, 610.0),
    ("PAGEIND", "Page Industries Ltd.", "Textiles", 0, 44200.0),
    ("TATACOMM", "Tata Communications Ltd.", "Telecom", 0, 1840.0),
    ("INDUSTOWER", "Indus Towers Ltd.", "Telecom Infra", 0, 355.0),
    ("CONCOR", "Container Corp. of India", "Logistics", 0, 860.0),
    ("PAYTM", "One97 Communications", "Fintech", 0, 780.0),
    ("POLICYBZR", "PB Fintech Ltd.", "Fintech", 0, 1680.0),
    ("IDEA", "Vodafone Idea Ltd.", "Telecom", 0, 7.80),
    ("SUZLON", "Suzlon Energy Ltd.", "Renewables", 0, 68.0),
    ("RVNL", "Rail Vikas Nigam Ltd.", "Railways", 0, 465.0),
    ("IRFC", "Indian Railway Finance", "Railways", 0, 155.0),
    ("IREDA", "Indian Renewable Energy Dev", "Renewables", 0, 210.0),
    ("MAZDOCK", "Mazagon Dock Shipbuilders", "Defense", 0, 4250.0),
    ("COCHINSHIP", "Cochin Shipyard Ltd.", "Defense", 0, 1580.0),
    ("HUDCO", "Housing & Urban Dev Corp", "NBFC", 0, 215.0),
    ("TATAELXSI", "Tata Elxsi Ltd.", "IT Design", 0, 6950.0),
    ("OFSS", "Oracle Financial Services", "IT Software", 0, 11400.0),
    ("CYIENT", "Cyient Ltd.", "IT Services", 0, 1820.0),
    ("ASTRAL", "Astral Ltd.", "Pipes", 0, 1840.0),
    ("SUPREMEIND", "Supreme Industries Ltd.", "Plastics", 0, 4650.0),
    ("ATGL", "Adani Total Gas Ltd.", "Gas Distribution", 0, 680.0),
    ("ADANIGREEN", "Adani Green Energy Ltd.", "Renewables", 0, 1560.0),
    ("ADANIPOWER", "Adani Power Ltd.", "Power", 0, 610.0),
    ("UBL", "United Breweries Ltd.", "Beverages", 0, 1980.0),
    ("MCDOWELL-N", "United Spirits Ltd.", "Beverages", 0, 1480.0),
    ("COROMANDEL", "Coromandel International", "Agrochem", 0, 1720.0),
    ("PRESTIGE", "Prestige Estates Projects", "Real Estate", 0, 1680.0),
    ("BRIGADE", "Brigade Enterprises Ltd.", "Real Estate", 0, 1240.0),
    ("PHOENIXLTD", "The Phoenix Mills Ltd.", "Real Estate", 0, 1620.0),
    ("SUNTV", "Sun TV Network Ltd.", "Media", 0, 760.0),
    ("ZEEL", "Zee Entertainment Ent.", "Media", 0, 125.0),
    ("PVRINOX", "PVR INOX Ltd.", "Media", 0, 1420.0),
    ("NAVINFLUOR", "Navin Fluorine Int.", "Chemicals", 0, 3350.0),
    ("JIOFIN", "Jio Financial Services", "Fintech/NBFC", 0, 315.0),
    ("ANGELONE", "Angel One Ltd.", "Brokerage", 0, 2850.0),
    ("POONAWALLA", "Poonawalla Fincorp Ltd.", "NBFC", 0, 365.0),
    ("LICHSGFIN", "LIC Housing Finance Ltd.", "NBFC", 0, 640.0),
    ("KIMS", "Krishna Inst of Medical Sci", "Hospitals", 0, 560.0),
    ("MEDANTA", "Global Health Ltd.", "Hospitals", 0, 1180.0),
    ("VBL", "Varun Beverages Ltd.", "Beverages", 0, 590.0),
    ("PRAJIND", "Praj Industries Ltd.", "Clean Energy", 0, 740.0),
    ("CEATLTD", "CEAT Ltd.", "Tyres", 0, 2840.0),
    ("RITES", "RITES Ltd.", "Railways", 0, 310.0),
    ("IRCON", "Ircon International Ltd.", "Railways", 0, 220.0),
    ("TITAGARH", "Titagarh Rail Systems", "Railways", 0, 1280.0),
    ("KAYNES", "Kaynes Technology India", "Electronics", 0, 5450.0),
    ("HDFCAMC", "HDFC Asset Management", "Asset Mgmt", 0, 4350.0)
]

def sync_universe_to_db():
    """Populates the symbols_universe table if empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM symbols_universe")
        count = cursor.fetchone()[0]
        if count < len(DEFAULT_NSE_FNO_UNIVERSE):
            for sym, name, sector, n50, price in DEFAULT_NSE_FNO_UNIVERSE:
                cursor.execute("""
                INSERT OR REPLACE INTO symbols_universe 
                (symbol, company_name, sector, is_fno, is_nifty50, base_price)
                VALUES (?, ?, ?, 1, ?, ?)
                """, (sym, name, sector, n50, price))
            conn.commit()

sync_universe_to_db()

# -----------------------------------------------------------------------------
# 4. QUANT MATCHING & PERSISTENCE ENGINE
# -----------------------------------------------------------------------------
def process_daily_session(trade_date: str, quotes_df: pd.DataFrame, top_n: int = 10) -> Dict:
    """
    Ranks the universe, updates persistence streak counters, archives exited runners,
    and logs Day-1 additions into market_streaks.db.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Clean & Vectorize Quotes
    quotes_df = quotes_df.copy()
    quotes_df['trade_date'] = trade_date
    quotes_df['pct_change'] = ((quotes_df['close'] - quotes_df['prev_close']) / quotes_df['prev_close']) * 100.0
    quotes_df['pct_change'] = quotes_df['pct_change'].round(2)
    
    # Insert quotes into daily_quotes
    records = []
    for _, row in quotes_df.iterrows():
        records.append((
            trade_date, row['symbol'], float(row['open']), float(row['high']),
            float(row['low']), float(row['close']), float(row['prev_close']),
            float(row['pct_change']), int(row.get('volume', 100000))
        ))
    cursor.executemany("""
    INSERT OR REPLACE INTO daily_quotes 
    (trade_date, symbol, open, high, low, close, prev_close, pct_change, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    # 2. Extract Top N Gainers & Losers
    top_gainers = quotes_df.sort_values(by='pct_change', ascending=False).head(top_n).reset_index(drop=True)
    top_losers = quotes_df.sort_values(by='pct_change', ascending=True).head(top_n).reset_index(drop=True)

    # Delete any existing rankings for this date to avoid duplication
    cursor.execute("DELETE FROM daily_top_movers WHERE trade_date = ?", (trade_date,))
    cursor.execute("DELETE FROM churn_events WHERE trade_date = ?", (trade_date,))

    for idx, row in top_gainers.iterrows():
        cursor.execute("""
        INSERT INTO daily_top_movers (trade_date, category, rank, symbol, pct_change, close, prev_close)
        VALUES (?, 'GAINER', ?, ?, ?, ?, ?)
        """, (trade_date, idx + 1, row['symbol'], row['pct_change'], row['close'], row['prev_close']))

    for idx, row in top_losers.iterrows():
        cursor.execute("""
        INSERT INTO daily_top_movers (trade_date, category, rank, symbol, pct_change, close, prev_close)
        VALUES (?, 'LOSER', ?, ?, ?, ?, ?)
        """, (trade_date, idx + 1, row['symbol'], row['pct_change'], row['close'], row['prev_close']))

    # 3. Retrieve currently ACTIVE streaks from registry
    cursor.execute("SELECT * FROM streak_registry WHERE status = 'ACTIVE'")
    active_rows = cursor.fetchall()
    active_streaks = {row['symbol']: dict(row) for row in active_rows}

    today_gainers_syms = set(top_gainers['symbol'])
    today_losers_syms = set(top_losers['symbol'])

    # 4. Match GAINERS
    for idx, row in top_gainers.iterrows():
        sym = row['symbol']
        close_p = float(row['close'])
        prev_p = float(row['prev_close'])
        daily_pct = float(row['pct_change'])
        rank = idx + 1

        if sym in active_streaks and active_streaks[sym]['category'] == 'GAINER':
            # Streak CONTINUES!
            stk = active_streaks[sym]
            new_days = stk['streak_days'] + 1
            entry_p = stk['entry_price']
            cum_pct = round(((close_p - entry_p) / entry_p) * 100.0, 2)

            cursor.execute("""
            UPDATE streak_registry
            SET last_date = ?, streak_days = ?, last_price = ?, cum_return_pct = ?
            WHERE streak_id = ?
            """, (trade_date, new_days, close_p, cum_pct, stk['streak_id']))

            cursor.execute("""
            INSERT OR REPLACE INTO streak_snapshots 
            (streak_id, trade_date, day_index, symbol, close, daily_pct, cum_pct, rank_on_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (stk['streak_id'], trade_date, new_days, sym, close_p, daily_pct, cum_pct, rank))

            del active_streaks[sym]
        else:
            # NEW ENTRANT (Day 1)
            streak_id = f"STRK_GAIN_{sym}_{trade_date.replace('-', '')}"
            entry_p = prev_p  # Benchmark base price before breakout
            cum_pct = daily_pct

            cursor.execute("""
            INSERT OR REPLACE INTO streak_registry
            (streak_id, symbol, category, start_date, last_date, streak_days, entry_price, last_price, cum_return_pct, status)
            VALUES (?, ?, 'GAINER', ?, ?, 1, ?, ?, ?, 'ACTIVE')
            """, (streak_id, sym, trade_date, trade_date, entry_p, close_p, cum_pct))

            cursor.execute("""
            INSERT OR REPLACE INTO streak_snapshots 
            (streak_id, trade_date, day_index, symbol, close, daily_pct, cum_pct, rank_on_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (streak_id, trade_date, 1, sym, close_p, daily_pct, cum_pct, rank))

            cursor.execute("""
            INSERT OR REPLACE INTO churn_events
            (trade_date, symbol, event_type, category, streak_days, return_pct, exit_price, entry_price)
            VALUES (?, ?, 'NEW_ENTRANT', 'GAINER', 1, ?, ?, ?)
            """, (trade_date, sym, cum_pct, close_p, entry_p))

    # 5. Match LOSERS
    for idx, row in top_losers.iterrows():
        sym = row['symbol']
        close_p = float(row['close'])
        prev_p = float(row['prev_close'])
        daily_pct = float(row['pct_change'])
        rank = idx + 1

        if sym in active_streaks and active_streaks[sym]['category'] == 'LOSER':
            # Drawdown streak CONTINUES!
            stk = active_streaks[sym]
            new_days = stk['streak_days'] + 1
            entry_p = stk['entry_price']
            cum_pct = round(((close_p - entry_p) / entry_p) * 100.0, 2)

            cursor.execute("""
            UPDATE streak_registry
            SET last_date = ?, streak_days = ?, last_price = ?, cum_return_pct = ?
            WHERE streak_id = ?
            """, (trade_date, new_days, close_p, cum_pct, stk['streak_id']))

            cursor.execute("""
            INSERT OR REPLACE INTO streak_snapshots 
            (streak_id, trade_date, day_index, symbol, close, daily_pct, cum_pct, rank_on_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (stk['streak_id'], trade_date, new_days, sym, close_p, daily_pct, cum_pct, rank))

            del active_streaks[sym]
        else:
            # NEW ENTRANT (Day 1 Loser)
            streak_id = f"STRK_LOSS_{sym}_{trade_date.replace('-', '')}"
            entry_p = prev_p
            cum_pct = daily_pct

            cursor.execute("""
            INSERT OR REPLACE INTO streak_registry
            (streak_id, symbol, category, start_date, last_date, streak_days, entry_price, last_price, cum_return_pct, status)
            VALUES (?, ?, 'LOSER', ?, ?, 1, ?, ?, ?, 'ACTIVE')
            """, (streak_id, sym, trade_date, trade_date, entry_p, close_p, cum_pct))

            cursor.execute("""
            INSERT OR REPLACE INTO streak_snapshots 
            (streak_id, trade_date, day_index, symbol, close, daily_pct, cum_pct, rank_on_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (streak_id, trade_date, 1, sym, close_p, daily_pct, cum_pct, rank))

            cursor.execute("""
            INSERT OR REPLACE INTO churn_events
            (trade_date, symbol, event_type, category, streak_days, return_pct, exit_price, entry_price)
            VALUES (?, ?, 'NEW_ENTRANT', 'LOSER', 1, ?, ?, ?)
            """, (trade_date, sym, cum_pct, close_p, entry_p))

    # 6. Any remaining active stocks from yesterday that are NOT in today's top list -> EXITED!
    for sym, stk in active_streaks.items():
        # Get today's quote if available
        today_match = quotes_df[quotes_df['symbol'] == sym]
        if not today_match.empty:
            exit_p = float(today_match.iloc[0]['close'])
            entry_p = stk['entry_price']
            realized_return = round(((exit_p - entry_p) / entry_p) * 100.0, 2)
        else:
            exit_p = stk['last_price']
            realized_return = stk['cum_return_pct']

        cursor.execute("""
        UPDATE streak_registry
        SET status = 'EXITED', last_date = ?
        WHERE streak_id = ?
        """, (trade_date, stk['streak_id']))

        cursor.execute("""
        INSERT OR REPLACE INTO churn_events
        (trade_date, symbol, event_type, category, streak_days, return_pct, exit_price, entry_price)
        VALUES (?, ?, 'EXITED', ?, ?, ?, ?, ?)
        """, (trade_date, sym, stk['category'], stk['streak_days'], realized_return, exit_p, stk['entry_price']))

    # 7. Log pipeline audit
    cursor.execute("""
    INSERT INTO pipeline_audit (timestamp, event_name, status, details, records_count)
    VALUES (?, 'SESSION_PROCESSED', 'SUCCESS', ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Date: {trade_date} Top-N: {top_n}", len(quotes_df)))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "trade_date": trade_date,
        "processed_symbols": len(quotes_df),
        "top_gainers_count": len(top_gainers),
        "top_losers_count": len(top_losers)
    }
# -----------------------------------------------------------------------------
# 5. HISTORICAL REALISTIC DATA SEEDER & SIMULATION ENGINE
# -----------------------------------------------------------------------------
def seed_historical_market_data(num_sessions: int = 10, force: bool = False):
    """
    Populates realistic multi-session historical data with active streaks,
    exits, and day-1 additions so the dashboard displays authentic multi-day data.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT trade_date) FROM daily_quotes")
        existing_days = cursor.fetchone()[0]

    if existing_days >= num_sessions and not force:
        return

    # Clear existing streak tables if force resetting
    if force:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM daily_quotes")
            cursor.execute("DELETE FROM daily_top_movers")
            cursor.execute("DELETE FROM streak_registry")
            cursor.execute("DELETE FROM streak_snapshots")
            cursor.execute("DELETE FROM churn_events")
            cursor.execute("DELETE FROM pipeline_audit")
            conn.commit()

    # Generate dates backwards from today, excluding weekends
    dates = []
    curr = date.today()
    while len(dates) < num_sessions:
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr.strftime("%Y-%m-%d"))
        curr -= timedelta(days=1)
    dates.reverse()

    # Load Universe
    with get_db_connection() as conn:
        df_uni = pd.read_sql("SELECT symbol, base_price FROM symbols_universe", conn)

    np.random.seed(42)  # Deterministic seed for reproducible streaks
    symbols = df_uni['symbol'].tolist()
    current_prices = {row['symbol']: float(row['base_price']) for _, row in df_uni.iterrows()}

    # Designate specific persistent runners to guarantee realistic multi-day streaks
    # TRENT: 4-day active gainer surge
    # HAL: 3-day active gainer rally
    # DIXON: 2-day active gainer
    # IDEA: 3-day active loser slide
    # PAYTM: 2-day active loser
    # BHEL: Ran for 3 days and exited today!
    # ZEEL: Ran for 2 days drawdown and exited today!
    
    for i, t_date in enumerate(dates):
        quotes = []
        is_today = (i == len(dates) - 1)
        is_yesterday = (i == len(dates) - 2)
        is_2days_ago = (i == len(dates) - 3)
        is_3days_ago = (i == len(dates) - 4)

        for sym in symbols:
            prev_close = current_prices[sym]
            
            # Baseline market drift: mean 0.1%, vol 1.8%
            pct = np.random.normal(0.1, 1.8)

            # Inject controlled momentum for designated streak leaders
            if sym == "TRENT" and i >= len(dates) - 4:
                pct = np.random.uniform(3.8, 6.2)   # 4 consecutive days in Top Gainers
            elif sym == "HAL" and i >= len(dates) - 3:
                pct = np.random.uniform(3.5, 5.5)   # 3 consecutive days in Top Gainers
            elif sym == "DIXON" and i >= len(dates) - 2:
                pct = np.random.uniform(3.2, 5.0)   # 2 consecutive days in Top Gainers
            elif sym == "BEL" and is_today:
                pct = 6.45                          # Day 1 New Entrant Gainer today!
            elif sym == "TATASTEEL" and is_today:
                pct = 5.20                          # Day 1 New Entrant Gainer today!
            elif sym == "COALINDIA" and is_today:
                pct = 4.85                          # Day 1 New Entrant Gainer today!
            elif sym == "BHEL":
                if is_3days_ago or is_2days_ago or is_yesterday:
                    pct = np.random.uniform(4.0, 5.8)  # Top gainer past 3 days
                elif is_today:
                    pct = -0.65                     # Exited top gainers today!
            elif sym == "IDEA" and i >= len(dates) - 3:
                pct = np.random.uniform(-4.5, -6.5) # 3 consecutive days in Top Losers
            elif sym == "PAYTM" and i >= len(dates) - 2:
                pct = np.random.uniform(-3.5, -5.2) # 2 consecutive days in Top Losers
            elif sym == "BERGEPAINT" and i >= len(dates) - 2:
                pct = np.random.uniform(-3.0, -4.6) # 2 consecutive days in Top Losers
            elif sym == "INDUSINDBK" and is_today:
                pct = -4.75                         # Day 1 New Entrant Loser today!
            elif sym == "HINDALCO" and is_today:
                pct = -3.90                         # Day 1 New Entrant Loser today!
            elif sym == "ZEEL":
                if is_2days_ago or is_yesterday:
                    pct = np.random.uniform(-4.0, -5.5)
                elif is_today:
                    pct = 0.40                      # Exited top losers today!

            close = round(prev_close * (1 + pct / 100.0), 2)
            high = round(max(close, prev_close) * (1 + abs(np.random.normal(0.005, 0.003))), 2)
            low = round(min(close, prev_close) * (1 - abs(np.random.normal(0.005, 0.003))), 2)
            open_p = round(prev_close * (1 + np.random.normal(0.0, 0.004)), 2)
            vol = int(np.random.uniform(150000, 3500000))

            current_prices[sym] = close
            quotes.append({
                'symbol': sym,
                'open': open_p,
                'high': high,
                'low': low,
                'close': close,
                'prev_close': prev_close,
                'volume': vol
            })

        df_day = pd.DataFrame(quotes)
        process_daily_session(t_date, df_day, top_n=10)

# Auto-seed on first launch if database has fewer than 5 trading days
seed_historical_market_data(num_sessions=10, force=False)

# -----------------------------------------------------------------------------
# 6. LIVE EOD DATA PIPELINE & SCHEDULER
# -----------------------------------------------------------------------------
def fetch_live_eod_data() -> Tuple[bool, str]:
    """
    Attempts to download today's official NSE Bhavcopy from official archives.
    Falls back gracefully if the market is active, weekend, or offline.
    """
    today_str = date.today().strftime("%d-%m-%Y")
    today_iso = date.today().strftime("%Y-%m-%d")
    now_ist = datetime.now()
    
    # Check trading time
    if now_ist.weekday() >= 5:
        return False, f"Today is {now_ist.strftime('%A')} (NSE Weekend Closed). Official Bhavcopy is generated Mon-Fri post 4:30 PM IST."
    
    if now_ist.hour < 15 or (now_ist.hour == 15 and now_ist.minute < 30):
        # Market still running
        return False, f"NSE Live Market is currently ACTIVE (Closes at 3:30 PM IST). Official EOD Bhavcopy publishes post 4:30 PM IST. Current time: {now_ist.strftime('%H:%M:%S')} IST."

    # Strategy 1: Attempt nselib bhavcopy
    try:
        from nselib import capital_market
        df = capital_market.bhav_copy_equities(today_str)
        if df is not None and not df.empty:
            # Map columns
            df.columns = [c.strip().upper() for c in df.columns]
            if 'SERIES' in df.columns:
                df = df[df['SERIES'] == 'EQ']
            
            # Map required columns
            df = df.rename(columns={
                'SYMBOL': 'symbol', 'CLOSE': 'close', 'PREVCLOSE': 'prev_close',
                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'TOTTRDQTY': 'volume'
            })
            
            # Filter to our universe symbols
            with get_db_connection() as conn:
                valid_syms = set(pd.read_sql("SELECT symbol FROM symbols_universe", conn)['symbol'])
            
            df_filtered = df[df['symbol'].isin(valid_syms)]
            if not df_filtered.empty:
                process_daily_session(today_iso, df_filtered, top_n=10)
                return True, f"Successfully fetched and ingested official NSE Bhavcopy for {today_iso} ({len(df_filtered)} scrips)."
    except Exception as e:
        # Fall through to secondary methods
        pass

    # Strategy 2: Direct NSE Bhavcopy ZIP
    try:
        date_tag = date.today().strftime("%Y%m%d")
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_tag}_F_0000.csv.zip"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                for filename in z.namelist():
                    if filename.endswith(".csv"):
                        with z.open(filename) as f:
                            bhav = pd.read_csv(f)
                            bhav.columns = [c.strip().upper() for c in bhav.columns]
                            if 'SERIES' in bhav.columns:
                                bhav = bhav[bhav['SERIES'] == 'EQ']
                            bhav = bhav.rename(columns={
                                'SYMBOL': 'symbol', 'CLOSE': 'close', 'PREVCLOSE': 'prev_close',
                                'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'TOTTRDQTY': 'volume'
                            })
                            with get_db_connection() as conn:
                                valid_syms = set(pd.read_sql("SELECT symbol FROM symbols_universe", conn)['symbol'])
                            bhav_filtered = bhav[bhav['symbol'].isin(valid_syms)]
                            if not bhav_filtered.empty:
                                process_daily_session(today_iso, bhav_filtered, top_n=10)
                                return True, f"Successfully pulled direct NSE Bhavcopy archive for {today_iso}."
    except Exception:
        pass

    return False, f"Could not reach external NSE Bhavcopy endpoint (Server may require direct broadband ISP or session token). Use the 'Simulate Next Trading Day' feature to test live multi-session streak persistence immediately."

def simulate_advance_trading_day() -> str:
    """Simulates an advanced business trading day with authentic market volatility."""
    with get_db_connection() as conn:
        latest_date_row = conn.execute("SELECT MAX(trade_date) FROM daily_quotes").fetchone()
        latest_date_str = latest_date_row[0] if latest_date_row else date.today().strftime("%Y-%m-%d")
        
        # Get quotes of the latest date
        df_latest = pd.read_sql("SELECT symbol, close FROM daily_quotes WHERE trade_date = ?", conn, params=(latest_date_str,))
        if df_latest.empty:
            df_latest = pd.read_sql("SELECT symbol, base_price as close FROM symbols_universe", conn)

    # Next business day
    next_date = datetime.strptime(latest_date_str, "%Y-%m-%d").date() + timedelta(days=1)
    while next_date.weekday() >= 5:  # Skip weekends
        next_date += timedelta(days=1)
    next_date_str = next_date.strftime("%Y-%m-%d")

    quotes = []
    for _, row in df_latest.iterrows():
        sym = row['symbol']
        prev_close = float(row['close'])
        # Realistic fat-tailed distribution with occasional breakouts
        pct = np.random.laplace(0.1, 1.9)
        # Cap daily circuits at ±10% for realistic F&O dynamics
        pct = np.clip(pct, -9.8, 9.8)
        close = round(prev_close * (1 + pct / 100.0), 2)
        high = round(max(close, prev_close) * (1 + abs(np.random.normal(0.005, 0.003))), 2)
        low = round(min(close, prev_close) * (1 - abs(np.random.normal(0.005, 0.003))), 2)
        open_p = round(prev_close * (1 + np.random.normal(0.0, 0.004)), 2)
        vol = int(np.random.uniform(200000, 4500000))

        quotes.append({
            'symbol': sym,
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'prev_close': prev_close,
            'volume': vol
        })

    df_next = pd.DataFrame(quotes)
    process_daily_session(next_date_str, df_next, top_n=10)
    return next_date_str

# Background Scheduler Thread Setup
class BackgroundScheduler(threading.Thread):
    def __init__(self, target_hour=16, target_minute=0):
        super().__init__(daemon=True)
        self.target_hour = target_hour
        self.target_minute = target_minute
        self.running = True

    def run(self):
        while self.running:
            try:
                now = datetime.now()
                # Run if weekday and time >= 16:00 IST
                if now.weekday() < 5 and now.hour == self.target_hour and now.minute == self.target_minute:
                    today_iso = now.strftime("%Y-%m-%d")
                    with get_db_connection() as conn:
                        res = conn.execute("SELECT 1 FROM daily_quotes WHERE trade_date = ? LIMIT 1", (today_iso,)).fetchone()
                    if not res:
                        fetch_live_eod_data()
                        time.sleep(70)  # avoid double trigger within same minute
            except Exception:
                pass
            time.sleep(30)

@st.cache_resource
def start_scheduler():
    scheduler = BackgroundScheduler(target_hour=16, target_minute=0)
    scheduler.start()
    return scheduler

scheduler_instance = start_scheduler()

# -----------------------------------------------------------------------------
# 7. DATA ACCESS & STREAK ANALYTICS HELPERS
# -----------------------------------------------------------------------------
def get_available_dates() -> List[str]:
    """Returns sorted list of all trade dates in database (most recent first)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT trade_date FROM daily_quotes ORDER BY trade_date DESC")
        dates = [row[0] for row in cursor.fetchall()]
    return dates

def get_dashboard_data(selected_date: str) -> Dict:
    """
    Extracts structured data for the 4 zones for the selected session date.
    Zone 1: Active Gainer Streaks (Streak >= 2)
    Zone 2: Active Loser Streaks (Streak >= 2)
    Zone 3: Exited Stocks (Exited from yesterday's pool today)
    Zone 4: New Entrants (Day 1 additions today)
    """
    with get_db_connection() as conn:
        # 1. Top Gainers today with streak info
        q_gainers = """
        SELECT 
            m.rank, m.symbol, u.company_name, u.sector,
            q.close, q.prev_close, q.pct_change,
            r.streak_days, r.entry_price, r.cum_return_pct, r.start_date,
            (SELECT prev_q.pct_change FROM daily_quotes prev_q 
             WHERE prev_q.symbol = m.symbol 
               AND prev_q.trade_date < m.trade_date 
             ORDER BY prev_q.trade_date DESC LIMIT 1) as prev_day_pct
        FROM daily_top_movers m
        JOIN symbols_universe u ON m.symbol = u.symbol
        JOIN daily_quotes q ON m.trade_date = q.trade_date AND m.symbol = q.symbol
        LEFT JOIN streak_registry r ON m.symbol = r.symbol AND r.status = 'ACTIVE'
        WHERE m.trade_date = ? AND m.category = 'GAINER'
        ORDER BY m.rank ASC
        """
        gainers_df = pd.read_sql(q_gainers, conn, params=(selected_date,))

        # 2. Top Losers today with streak info
        q_losers = """
        SELECT 
            m.rank, m.symbol, u.company_name, u.sector,
            q.close, q.prev_close, q.pct_change,
            r.streak_days, r.entry_price, r.cum_return_pct, r.start_date,
            (SELECT prev_q.pct_change FROM daily_quotes prev_q 
             WHERE prev_q.symbol = m.symbol 
               AND prev_q.trade_date < m.trade_date 
             ORDER BY prev_q.trade_date DESC LIMIT 1) as prev_day_pct
        FROM daily_top_movers m
        JOIN symbols_universe u ON m.symbol = u.symbol
        JOIN daily_quotes q ON m.trade_date = q.trade_date AND m.symbol = q.symbol
        LEFT JOIN streak_registry r ON m.symbol = r.symbol AND r.status = 'ACTIVE'
        WHERE m.trade_date = ? AND m.category = 'LOSER'
        ORDER BY m.rank ASC
        """
        losers_df = pd.read_sql(q_losers, conn, params=(selected_date,))

        # 3. Exited Stocks today (Churn Event = 'EXITED')
        q_exited = """
        SELECT 
            c.symbol, u.company_name, u.sector, c.category,
            c.streak_days, c.return_pct, c.exit_price, c.entry_price
        FROM churn_events c
        JOIN symbols_universe u ON c.symbol = u.symbol
        WHERE c.trade_date = ? AND c.event_type = 'EXITED'
        ORDER BY c.streak_days DESC, ABS(c.return_pct) DESC
        """
        exited_df = pd.read_sql(q_exited, conn, params=(selected_date,))

        # 4. New Entrants today (Day 1 Streaks)
        q_entrants = """
        SELECT 
            c.symbol, u.company_name, u.sector, c.category,
            c.streak_days, c.return_pct, c.exit_price as close, c.entry_price as prev_close,
            m.rank
        FROM churn_events c
        JOIN symbols_universe u ON c.symbol = u.symbol
        LEFT JOIN daily_top_movers m ON c.trade_date = m.trade_date AND c.symbol = m.symbol
        WHERE c.trade_date = ? AND c.event_type = 'NEW_ENTRANT'
        ORDER BY m.rank ASC
        """
        entrants_df = pd.read_sql(q_entrants, conn, params=(selected_date,))

    # Partition Zone 1 & 2: Active Multi-Day Streaks (streak_days >= 2)
    # Day-1 stocks automatically show in Zone 4 (New Entrants)
    active_gainers = gainers_df[gainers_df['streak_days'] >= 2].copy()
    active_losers = losers_df[losers_df['streak_days'] >= 2].copy()

    return {
        "active_gainers": active_gainers,
        "active_losers": active_losers,
        "exited": exited_df,
        "entrants": entrants_df,
        "all_gainers": gainers_df,
        "all_losers": losers_df
    }

def get_stock_drilldown_data(symbol: str) -> Optional[Dict]:
    """Retrieves full historical performance and streak timeline for a given stock."""
    with get_db_connection() as conn:
        # Stock master
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM symbols_universe WHERE symbol = ?", (symbol,))
        stock_meta = cursor.fetchone()
        if not stock_meta:
            return None

        # Price history across all dates
        quotes_df = pd.read_sql("""
        SELECT trade_date, open, high, low, close, prev_close, pct_change, volume
        FROM daily_quotes
        WHERE symbol = ?
        ORDER BY trade_date ASC
        """, conn, params=(symbol,))

        # Active or most recent streak
        cursor.execute("""
        SELECT * FROM streak_registry
        WHERE symbol = ?
        ORDER BY last_date DESC LIMIT 1
        """, (symbol,))
        streak_meta = cursor.fetchone()

        # Streak snapshots
        snapshots_df = pd.DataFrame()
        if streak_meta:
            snapshots_df = pd.read_sql("""
            SELECT trade_date, day_index, close, daily_pct, cum_pct, rank_on_day
            FROM streak_snapshots
            WHERE streak_id = ?
            ORDER BY day_index ASC
            """, conn, params=(streak_meta['streak_id'],))

    return {
        "meta": dict(stock_meta),
        "streak": dict(streak_meta) if streak_meta else None,
        "quotes": quotes_df,
        "snapshots": snapshots_df
    }

# -----------------------------------------------------------------------------
# 8. SIDEBAR CONTROLS & MARKET HEALTH
# -----------------------------------------------------------------------------
dates_list = get_available_dates()
if not dates_list:
    st.error("No market session data found in SQLite. Please click 'Seed Historical Data'.")
    st.stop()

selected_date = st.sidebar.selectbox(
    "📅 Select Trading Session (EOD)",
    options=dates_list,
    index=0,
    help="Select any date to inspect multi-day streaks and churn events on that session."
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Data Automation & Ingestion")

col_fetch, col_sim = st.sidebar.columns(2)
with col_fetch:
    if st.button("🔄 Fetch Today's EOD", use_container_width=True, help="Fetch latest official NSE Bhavcopy for today."):
        with st.spinner("Connecting to NSE Bhavcopy pipeline..."):
            success, msg = fetch_live_eod_data()
            if success:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.warning(msg)

with col_sim:
    if st.button("⏩ Advance Session", use_container_width=True, help="Simulate next business trading session."):
        new_date = simulate_advance_trading_day()
        st.sidebar.success(f"Generated Session: {new_date}")
        st.rerun()

if st.sidebar.button("🌱 Reset & Re-Seed 10 Sessions", use_container_width=True, help="Reset database with 10 deterministic realistic sessions."):
    with st.spinner("Populating 10 historical NSE trading sessions..."):
        seed_historical_market_data(num_sessions=10, force=True)
        st.sidebar.success("Database seeded successfully!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Quant Filters")
universe_choice = st.sidebar.radio(
    "Market Universe Scope",
    ["NSE F&O Equities (~185 Scrips)", "NIFTY 50 Bluechips", "Full Universe"],
    index=0
)
top_n = st.sidebar.slider("Top Movers Threshold (Top N)", min_value=5, max_value=20, value=10, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Background Post-Market Daemon")
st.sidebar.markdown("""
<div style="font-size: 12px; color: #94a3b8; line-height: 1.5;">
<strong>Status:</strong> <span style="color: #34d399;">● Running (Daemon)</span><br>
<strong>Target Trigger:</strong> 16:00 IST (Post-Close)<br>
<strong>Storage:</strong> 100% Private Local SQLite (market_streaks.db)
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. MAIN DASHBOARD: 4-ZONE ARCHITECTURE
# -----------------------------------------------------------------------------
# Load Data for Selected Session
dash_data = get_dashboard_data(selected_date)
active_gainers = dash_data['active_gainers']
active_losers = dash_data['active_losers']
exited_stocks = dash_data['exited']
new_entrants = dash_data['entrants']

# Header & KPI Strip
st.markdown(f"""
<div class="main-header">
    <h1><span>⚡</span> NSE Ultimate Momentum & Streak Tracker Dashboard</h1>
    <p>End-of-Day Multi-Session Persistence & Churn Intelligence Engine for Indian Equities & Derivatives</p>
    <div class="kpi-container">
        <div class="kpi-chip">
            <span class="kpi-chip-label">Trading Session</span>
            <span class="kpi-chip-val" style="color: #38bdf8;">{selected_date}</span>
        </div>
        <div class="kpi-chip">
            <span class="kpi-chip-label">Active Gainer Streaks</span>
            <span class="kpi-chip-val" style="color: #34d399;">{len(active_gainers)}</span>
        </div>
        <div class="kpi-chip">
            <span class="kpi-chip-label">Active Loser Streaks</span>
            <span class="kpi-chip-val" style="color: #f87171;">{len(active_losers)}</span>
        </div>
        <div class="kpi-chip">
            <span class="kpi-chip-label">Exited Yesterday's Run</span>
            <span class="kpi-chip-val" style="color: #fbbf24;">{len(exited_stocks)}</span>
        </div>
        <div class="kpi-chip">
            <span class="kpi-chip-label">New Entrants (Day 1)</span>
            <span class="kpi-chip-val" style="color: #818cf8;">{len(new_entrants)}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Manage inspection state
if "inspected_stock" not in st.session_state:
    # Default to first active gainer if present
    if not active_gainers.empty:
        st.session_state["inspected_stock"] = active_gainers.iloc[0]['symbol']
    elif not new_entrants.empty:
        st.session_state["inspected_stock"] = new_entrants.iloc[0]['symbol']
    else:
        st.session_state["inspected_stock"] = "TRENT"

# Render the 4 Side-by-Side Columns
col1, col2, col3, col4 = st.columns(4)

# -----------------------------------------------------------------------------
# ZONE 1: 🟢 TOP GAINERS (Active Multi-Day Streaks)
# -----------------------------------------------------------------------------
with col1:
    st.markdown("""
    <div class="zone-header zone-gainer">
        <span>🟢 ACTIVE GAINERS</span>
        <span style="font-size: 11px; opacity: 0.85;">Streak ≥ 2 Days</span>
    </div>
    """, unsafe_allow_html=True)

    if active_gainers.empty:
        st.markdown("""
        <div class="empty-zone">
            No continuing multi-day gainer streaks on this session. Check <strong>New Entrants</strong> column for Day-1 breakout runners!
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, row in active_gainers.iterrows():
            sym = row['symbol']
            days = int(row['streak_days']) if pd.notnull(row['streak_days']) else 2
            close = f"₹{row['close']:,.2f}"
            today_pct = f"+{row['pct_change']:.2f}%" if row['pct_change'] >= 0 else f"{row['pct_change']:.2f}%"
            prev_pct = f"+{row['prev_day_pct']:.2f}%" if pd.notnull(row['prev_day_pct']) and row['prev_day_pct'] >= 0 else (f"{row['prev_day_pct']:.2f}%" if pd.notnull(row['prev_day_pct']) else "N/A")
            cum_pct = f"+{row['cum_return_pct']:.2f}%" if pd.notnull(row['cum_return_pct']) and row['cum_return_pct'] >= 0 else (f"{row['cum_return_pct']:.2f}%" if pd.notnull(row['cum_return_pct']) else today_pct)

            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-card-top">
                    <div>
                        <div class="stock-symbol">{sym}</div>
                        <div class="stock-name" title="{row['company_name']}">{row['company_name']}</div>
                    </div>
                    <span class="badge badge-fire">🔥 {days} Days</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Close Price</span>
                        <span class="metric-val">{close}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Today's %</span>
                        <span class="metric-val green">{today_pct}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Prev Day %</span>
                        <span class="metric-val {'green' if '+' in prev_pct else 'red'}">{prev_pct}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Total Cumul %</span>
                        <span class="metric-val green">{cum_pct}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 Drilldown {sym}", key=f"btn_gainer_{sym}_{idx}", use_container_width=True):
                st.session_state["inspected_stock"] = sym
                st.rerun()

# -----------------------------------------------------------------------------
# ZONE 2: 🔴 TOP LOSERS (Active Multi-Day Streaks)
# -----------------------------------------------------------------------------
with col2:
    st.markdown("""
    <div class="zone-header zone-loser">
        <span>🔴 ACTIVE LOSERS</span>
        <span style="font-size: 11px; opacity: 0.85;">Streak ≥ 2 Days</span>
    </div>
    """, unsafe_allow_html=True)

    if active_losers.empty:
        st.markdown("""
        <div class="empty-zone">
            No continuing multi-day drawdown streaks on this session.
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, row in active_losers.iterrows():
            sym = row['symbol']
            days = int(row['streak_days']) if pd.notnull(row['streak_days']) else 2
            close = f"₹{row['close']:,.2f}"
            today_pct = f"{row['pct_change']:.2f}%"
            prev_pct = f"{row['prev_day_pct']:.2f}%" if pd.notnull(row['prev_day_pct']) else "N/A"
            cum_pct = f"{row['cum_return_pct']:.2f}%" if pd.notnull(row['cum_return_pct']) else today_pct

            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-card-top">
                    <div>
                        <div class="stock-symbol">{sym}</div>
                        <div class="stock-name" title="{row['company_name']}">{row['company_name']}</div>
                    </div>
                    <span class="badge badge-frost">❄️ {days} Days</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Close Price</span>
                        <span class="metric-val">{close}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Today's %</span>
                        <span class="metric-val red">{today_pct}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Prev Day %</span>
                        <span class="metric-val {'green' if '+' in prev_pct else 'red'}">{prev_pct}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Total Cumul Loss</span>
                        <span class="metric-val red">{cum_pct}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 Drilldown {sym}", key=f"btn_loser_{sym}_{idx}", use_container_width=True):
                st.session_state["inspected_stock"] = sym
                st.rerun()

# -----------------------------------------------------------------------------
# ZONE 3: 🟡 EXITED STOCKS (Dropped Out Today)
# -----------------------------------------------------------------------------
with col3:
    st.markdown("""
    <div class="zone-header zone-exit">
        <span>🟡 EXITED STOCKS</span>
        <span style="font-size: 11px; opacity: 0.85;">Dropped Out Today</span>
    </div>
    """, unsafe_allow_html=True)

    if exited_stocks.empty:
        st.markdown("""
        <div class="empty-zone">
            Zero churn exits on this session. All active momentum leaders persisted!
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, row in exited_stocks.iterrows():
            sym = row['symbol']
            cat = row['category']
            badge_class = "badge-exit-gainer" if cat == "GAINER" else "badge-exit-loser"
            badge_icon = "🚪 Exited Gainer" if cat == "GAINER" else "🚪 Exited Loser"
            days = int(row['streak_days'])
            ret_val = row['return_pct']
            ret_str = f"+{ret_val:.2f}%" if ret_val >= 0 else f"{ret_val:.2f}%"
            ret_color = "green" if ret_val >= 0 else "red"
            exit_p = f"₹{row['exit_price']:,.2f}"
            entry_p = f"₹{row['entry_price']:,.2f}"

            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-card-top">
                    <div>
                        <div class="stock-symbol">{sym}</div>
                        <div class="stock-name" title="{row['company_name']}">{row['company_name']}</div>
                    </div>
                    <span class="badge {badge_class}">{badge_icon}</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Run Duration</span>
                        <span class="metric-val">{days} Days Run</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Realized Return</span>
                        <span class="metric-val {ret_color}">{ret_str}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Exit Price</span>
                        <span class="metric-val">{exit_p}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Entry Price</span>
                        <span class="metric-val">{entry_p}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 History {sym}", key=f"btn_exit_{sym}_{idx}", use_container_width=True):
                st.session_state["inspected_stock"] = sym
                st.rerun()

#
-----------------------------------------------------------------------------
# ZONE 4: 🔵 NEW ENTRANTS (Day 1 Additions)
# -----------------------------------------------------------------------------
with col4:
    st.markdown("""
    <div class="zone-header zone-entrant">
        <span>🔵 NEW ENTRANTS</span>
        <span style="font-size: 11px; opacity: 0.85;">Day 1 Additions</span>
    </div>
    """, unsafe_allow_html=True)

    if new_entrants.empty:
        st.markdown("""
        <div class="empty-zone">
            No new additions today. All top movers are continuing streaks.
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, row in new_entrants.iterrows():
            sym = row['symbol']
            cat = row['category']
            badge_class = "badge-entrant-gainer" if cat == "GAINER" else "badge-entrant-loser"
            badge_icon = "⭐ Day 1 Gainer" if cat == "GAINER" else "⚠️ Day 1 Loser"
            close = f"₹{row['close']:,.2f}"
            ret_val = row['return_pct']
            ret_str = f"+{ret_val:.2f}%" if ret_val >= 0 else f"{ret_val:.2f}%"
            ret_color = "green" if ret_val >= 0 else "red"
            rank_str = f"Rank #{int(row['rank'])}" if pd.notnull(row['rank']) else "Top 10"

            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-card-top">
                    <div>
                        <div class="stock-symbol">{sym}</div>
                        <div class="stock-name" title="{row['company_name']}">{row['company_name']}</div>
                    </div>
                    <span class="badge {badge_class}">{badge_icon}</span>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Close Price</span>
                        <span class="metric-val">{close}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Today's Move</span>
                        <span class="metric-val {ret_color}">{ret_str}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Pool Standing</span>
                        <span class="metric-val">{rank_str}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Streak Status</span>
                        <span class="metric-val" style="color: #818cf8;">Day 1 Entry</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 Drilldown {sym}", key=f"btn_entrant_{sym}_{idx}", use_container_width=True):
                st.session_state["inspected_stock"] = sym
                st.rerun()

# -----------------------------------------------------------------------------
# 10. INTERACTIVE DRILL-DOWN MODAL & ANALYTICAL EXPANDER
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
inspected_sym = st.session_state.get("inspected_stock", "TRENT")

# Drilldown selector in case user wants to pick any tracked stock manually
all_universe_syms = sorted(list(set([row[0] for row in DEFAULT_NSE_FNO_UNIVERSE])))
c_label, c_select = st.columns([3, 1])
with c_label:
    st.markdown(f"### 🔬 Multi-Session Deep Drilldown: <span style='color: #38bdf8;'>{inspected_sym}</span>", unsafe_allow_html=True)
with c_select:
    new_pick = st.selectbox("Inspect Any Stock:", all_universe_syms, index=all_universe_syms.index(inspected_sym) if inspected_sym in all_universe_syms else 0, key="manual_pick")
    if new_pick != inspected_sym:
        st.session_state["inspected_stock"] = new_pick
        st.rerun()

drill_data = get_stock_drilldown_data(inspected_sym)

if drill_data and not drill_data['quotes'].empty:
    meta = drill_data['meta']
    streak = drill_data['streak']
    quotes = drill_data['quotes']
    snapshots = drill_data['snapshots']

    # 1. Streak Summary KPI Strip
    entry_date = streak['start_date'] if streak else "N/A"
    entry_price = streak['entry_price'] if streak else (quotes.iloc[0]['prev_close'] if not quotes.empty else 0.0)
    current_price = quotes.iloc[-1]['close'] if not quotes.empty else 0.0
    streak_days = streak['streak_days'] if streak else 1
    cum_return = round(((current_price - entry_price) / entry_price) * 100.0, 2) if entry_price > 0 else 0.0
    streak_status = streak['status'] if streak else "WATCHLIST"
    streak_cat = streak['category'] if streak else "NEUTRAL"

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Stock Symbol", f"{meta['symbol']}", meta.get('sector', 'NSE'))
    m2.metric("Entry Date", entry_date, f"{streak_status}")
    m3.metric("Entry Baseline", f"₹{entry_price:,.2f}")
    m4.metric("Current Close", f"₹{current_price:,.2f}", f"{quotes.iloc[-1]['pct_change']:.2f}% Today")
    m5.metric("Total Streak Days", f"{streak_days} Days", f"{streak_cat}")
    m6.metric("Net Cumulative Return", f"{cum_return:+.2f}%", delta=f"{cum_return:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Interactive Trend Line & Performance Chart (Plotly)
    t_tab1, t_tab2 = st.tabs(["📈 Interactive Price & Volume Chart", "📋 Day-by-Day Performance Table"])

    with t_tab1:
        # Build Dual Subplot Chart: Top for Price/Candles, Bottom for Volume & % Change
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.72, 0.28],
            subplot_titles=(f"{meta['company_name']} ({inspected_sym}) - Price Action & Streak Trajectory", "Daily % Change & Volume")
        )

        # Candlestick / Price Area
        fig.add_trace(
            go.Candlestick(
                x=quotes['trade_date'],
                open=quotes['open'],
                high=quotes['high'],
                low=quotes['low'],
                close=quotes['close'],
                name="OHLC Price",
                increasing_line_color="#10b981",
                decreasing_line_color="#ef4444"
            ),
            row=1, col=1
        )

        # Base entry price line
        fig.add_hline(
            y=entry_price,
            line_dash="dot",
            line_color="#94a3b8",
            annotation_text=f"Streak Entry Base: ₹{entry_price:,.2f}",
            annotation_position="bottom right",
            row=1, col=1
        )

        # Highlight streak points if available
        if not snapshots.empty:
            fig.add_trace(
                go.Scatter(
                    x=snapshots['trade_date'],
                    y=snapshots['close'],
                    mode='lines+markers',
                    name='Streak Run',
                    line=dict(color='#38bdf8', width=3),
                    marker=dict(size=9, color='#38bdf8', symbol='star')
                ),
                row=1, col=1
            )

        # Volume / Daily % Change bars on row 2
        bar_colors = ["#10b981" if p >= 0 else "#ef4444" for p in quotes['pct_change']]
        fig.add_trace(
            go.Bar(
                x=quotes['trade_date'],
                y=quotes['pct_change'],
                name="Daily % Move",
                marker_color=bar_colors,
                yaxis="y2"
            ),
            row=2, col=1
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(color="#94a3b8")
        )
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1, gridcolor="rgba(255,255,255,0.05)")
        fig.update_yaxes(title_text="Daily %", row=2, col=1, gridcolor="rgba(255,255,255,0.05)")
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")

        st.plotly_chart(fig, use_container_width=True)

    with t_tab2:
        # Day-by-Day Performance Table
        table_df = quotes.sort_values(by='trade_date', ascending=False).copy()
        
        # Calculate cumulative return from entry
        table_df['Cumulative %'] = (((table_df['close'] - entry_price) / entry_price) * 100.0).round(2)
        table_df['Status'] = "Broader Market"

        # Mark Streak active days
        if not snapshots.empty:
            streak_dates = set(snapshots['trade_date'])
            table_df['Status'] = table_df['trade_date'].apply(
                lambda d: f"🔥 Streak Day" if d in streak_dates else "Normal Session"
            )

        display_table = pd.DataFrame({
            "Date": table_df['trade_date'],
            "Closing Price (₹)": table_df['close'].apply(lambda x: f"₹{x:,.2f}"),
            "Daily % Change": table_df['pct_change'].apply(lambda x: f"{x:+.2f}%"),
            "Cumulative % Change": table_df['Cumulative %'].apply(lambda x: f"{x:+.2f}%"),
            "Traded Volume": table_df['volume'].apply(lambda x: f"{x:,.0f}"),
            "Streak Standing": table_df['Status']
        })

        st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True
        )
else:
    st.info(f"Select any stock card above or choose a symbol to inspect detailed streak analytics.")

# -----------------------------------------------------------------------------
# 11. FOOTER & AUDIT SUMMARY
# -----------------------------------------------------------------------------
st.markdown("---")
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    st.caption("NSE Ultimate Momentum & Streak Tracker | 100% Local Private SQLite Storage | Pure Python Streamlit")
with f2:
    st.caption(f"Connected Database: {os.path.basename(DB_FILE)}")
with f3:
    st.caption(f"IST Clock: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

