"""
This script takes in a ticker and outputs a dictionary containing the financials of every quarter for that ticker.
"""

import os
import sqlite3
import yfinance as yf
import streamlit as st


# Get the project root directory (3 levels up from src/data/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
finance_db = os.path.join(project_root, "util", "database", "finance.db")

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


import sqlite3

def extract_ticker_data(ticker, period):
    """
    Extracts financial data for a given ticker strictly before the given period.

    Args:
        ticker (str): Company ticker symbol (e.g. "AAPL").
        period (str): Cutoff period, formatted "Q<1–4> YYYY" (e.g. "Q3 2023").

    Returns:
        dict[str, dict[str, float]]: 
            A mapping from quarter string to a dict of { metric_name: value }.
            Only includes quarters < the cutoff period.
    """
    # Handle invalid or missing period
    if not period or not isinstance(period, str):
        return {}
    
    # Parse cutoff quarter & year
    try:
        parts = period.split()
        if len(parts) != 2:
            return {}
        
        cutoff_q_str, cutoff_year_str = parts
        
        # Validate quarter format
        if not cutoff_q_str.startswith('Q') or len(cutoff_q_str) != 2:
            return {}
        
        cutoff_year = int(cutoff_year_str)
        cutoff_q = int(cutoff_q_str.lstrip("Q"))
        
        # Validate quarter number
        if cutoff_q < 1 or cutoff_q > 4:
            return {}
            
    except (ValueError, AttributeError):
        return {}

    # Open and query
    try:
        # Check if database file exists
        if not os.path.exists(finance_db):
            return {}
            
        conn = sqlite3.connect(finance_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quarter, metric, value FROM financials WHERE ticker = ?",
            (ticker.upper(),)
        )
        rows = cursor.fetchall()
        conn.close()
    except (sqlite3.Error, Exception):
        return {}

    # Filter & structure
    data: dict[str, dict[str, float]] = {}
    for quarter_str, metric, value in rows:
        # parse each row’s quarter/year
        try:
            [q_str, year_str] = quarter_str.split()
            year = int(year_str)
            q = int(q_str.lstrip("Q"))
        except ValueError:
            # skip any malformed entries
            continue

        # include only if (year < cutoff_year) or (same year but q < cutoff_q)
        if (year < cutoff_year) or (year == cutoff_year and q < cutoff_q):
            data.setdefault(quarter_str, {})[metric] = value

    return data
def main():
    global conn, cursor
    # conn = sqlite3.connect(finance_db)
    # cursor = conn.cursor()
    
    # Example usage
    # st.write(extract_ticker_data("AAPL"))


if __name__ == "__main__":
    main()