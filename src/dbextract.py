"""
This script takes in a ticker and outputs a dictionary containing the financials of every quarter for that ticker.
"""

import os
import sqlite3
import yfinance as yf
import streamlit as st

finance_db = "../util/database/finance.db"

expected_output = {
    "Q1 2024": {
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
    },
    "Q2 2024": {
        "total revenue": 110000000000,
        "basic eps": 5.50,
        "dividend yield": 0.65,  
        "dividend rate": 0.35,  
        "ebitda": 33000000000,  
        "revenue growth": 12.0, 
        "ebitda margin": 32.0,  
        "net income": 22000000000, 
        "basic average shares": 15500000000, 
        "profit margin": 22.0, 
        "operating margin": 27.0
    },
    "Q3 2024": {
        "total revenue": 120000000000,
        "basic eps": 6.00,
        "dividend yield": 0.7,  
        "dividend rate": 0.40,  
        "ebitda": 36000000000,  
        "revenue growth": 15.0, 
        "ebitda margin": 35.0,  
        "net income": 24000000000, 
        "basic average shares": 16000000000, 
        "profit margin": 24.0, 
        "operating margin": 30.0
    },
    "Q4 2024": {
        "total revenue": 130000000000,
        "basic eps": 6.50,
        "dividend yield": 0.75,  
        "dividend rate": 0.45,  
        "ebitda": 39000000000,  
        "revenue growth": 18.0, 
        "ebitda margin": 38.0,  
        "net income": 26000000000, 
        "basic average shares": 16500000000, 
        "profit margin": 26.0, 
        "operating margin": 33.0
    },
    "Q1 2025": {
        "total revenue": 140000000000,
        "basic eps": 7.00,
        "dividend yield": 0.8,  
        "dividend rate": 0.50,  
        "ebitda": 42000000000,  
        "revenue growth": 20.0, 
        "ebitda margin": 40.0,  
        "net income": 28000000000, 
        "basic average shares": 17000000000, 
        "profit margin": 28.0, 
        "operating margin": 35.0
    }
}

def extract_ticker_data(ticker):
    """
    Extracts financial data for a given ticker from the SQLite database.
    
    Args:
        ticker (str): The stock ticker symbol.
    
    Returns:
        dict: A dictionary containing financial data for each quarter.
    """
    
    # Fetch all quarters for the given ticker
    cursor.execute('''
        SELECT quarter, metric, value FROM financials WHERE ticker = ?
    ''', (ticker,))
    
    rows = cursor.fetchall()
    
    # Process the fetched data into a structured dictionary
    data = {}
    for row in rows:
        quarter, metric, value = row
        if quarter not in data:
            data[quarter] = {}
        data[quarter][metric] = value
    
    conn.close()
    
    return data

def main():
    global conn, cursor
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()
    
    # Example usage
    st.write(extract_ticker_data("AAPL"))

    conn.close()

if __name__ == "__main__":
    main()