"""
This script updates a SQLite database with financial data for a specific company.
It takes a dictionary containing financial metrics and inserts them into the database.
"""

import os
import sqlite3
import yfinance as yf
import streamlit as st

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
    finance_db = "util/database/finance.db"
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()  
    # Insert financial data
    for metric, value in data.items():
        if metric != "ticker" and metric != "quarter":
            year = data.get("year")
            quarter = data.get("quarter")
            if quarter != None and year is not None:
                quarter_label = f"Q{quarter} {year}"
                cursor.execute('''
                    INSERT INTO financials (ticker, quarter, metric, value)
                    VALUES (?, ?, ?, ?)
                ''', (data["ticker"], quarter_label, metric, value))

    conn.commit()
    conn.close()


def main():
    global conn, cursor
    # update_db_from_dict(expected_output)


if __name__ == "__main__":
    main()