import os
import sqlite3
import yfinance as yf
import streamlit as st
import pandas as pd


included_metrics = ["total annual revenue",
           "basic EPS", 
           "dividend yield", 
           "dividend rate", 
           "ebitda", 
           "revenue growth", 
           "ebitda margin", 
           "net income", 
           "basic average shares", 
           "profit margin", 
           "operating margin"]


included_metrics = [m.strip() for m in included_metrics]

tickers = ["AAPL", "ATEC", "NESN", "TM", "MSFT"]

quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025"]


def create_table_financials():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            quarter TEXT,
            metric TEXT,
            value REAL
        )
    ''')
    conn.commit()


def create_table_quarter():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quarter TEXT NOT NULL
        )
    ''')

    for quarter in quarters:
        cursor.execute('''
            INSERT OR IGNORE INTO quarter (quarter) VALUES (?)
        ''', (quarter,))
    conn.commit()


def insert_data(ticker, quarter, metric, value):
    cursor.execute('''
        INSERT INTO financials (ticker, quarter, metric, value)
        VALUES (?, ?, ?, ?)
    ''', (ticker, quarter, metric, value))
    conn.commit()


def fill_db(ticker):
    dat = yf.Ticker(ticker)
    df = dat.quarterly_financials
    if df.empty:
        print(f"No financial data found for {ticker}.")
        return
    for row in df.index:
        if row.strip().lower() in included_metrics:
            for col in df.columns:
                value = df.loc[row, col]
                if pd.notna(value):
                    quarter_str = f"Q{((col.month - 1) // 3) + 1} {col.year}"
                    insert_data(ticker, quarter_str, row, value)


finance_db = "../util/database/finance.db"
db_exists = os.path.exists(finance_db)

def main():
    global conn, cursor
    
    if os.path.exists(finance_db):
        os.remove(finance_db)
        print("Old database deleted.")  
    
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()
    create_table_quarter()
    create_table_financials()
    for ticker in tickers:
        fill_db(ticker)
    conn.close()

if __name__ == "__main__":
    main()

