import os
import sqlite3
import yfinance as yf
import streamlit as st

finance_db = "../util/database/finance.db"

expected_output = {
    "ticker": "AAPL",
    "quarter": "Q2 2025",
    "total revenue": 100000000000,
    "basic eps": 5.00,
    "dividend yield": 0.6,  
    "dividend rate": 0.30,  
    "ebitda": 30000000000,  
    "revenue growth": 10.0, 
    "ebitda margin": 30.0,  
    "net income": 20000000000, 
    "basic average shares": 15000000000, 
    "profit margin": 20.0, 
    "operating margin": 25.0  
}

def update_db_from_dict(data):
    # Insert financial data
    for metric, value in data.items():
        if metric != "ticker" and metric != "quarter":
            cursor.execute('''
                INSERT INTO financials (ticker, quarter, metric, value)
                VALUES (?, ?, ?, ?)
            ''', (data["ticker"], data["quarter"], metric, value))

    conn.commit()

def main():
    global conn, cursor
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()  
    update_db_from_dict(expected_output)
    conn.close()


if __name__ == "__main__":
    main()