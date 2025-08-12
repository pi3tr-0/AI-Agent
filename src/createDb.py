"""
Creates a SQLite database for financial metrics of various companies.
This script fetches financial data from Yahoo Finance, processes it,
and stores it in a structured format in the database.
"""

import os
import sqlite3
import yfinance as yf
import streamlit as st
import pandas as pd

createdb_path = os.path.dirname(os.path.abspath(__file__))
finance_db = os.path.join(createdb_path, "../util/database/finance.db")

included_metrics = ["total revenue", #dollars
                   "basic eps", #dollars
                   "dividend yield", #percentage
                   "dividend rate", #dollars
                   "ebitda", #dollars
                   "revenue growth", #percentage
                   "ebitda margin", #percentage
                   "net income", #dollars
                   "basic average shares", #shares
                   "profit margin", #percentage
                   "operating margin"] #percentage

included_metrics = [m.strip() for m in included_metrics]

tickers = ["AAPL", "ATEC", "NESN", "TM", "MSFT", "AMZN", "NFLX"]

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


def create_table_financial_analysis():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quarter TEXT NOT NULL,
            analyst_name TEXT NOT NULL,
            price_target REAL,
            analyst_summary TEXT,
            performance_summary TEXT,
            investment_outlook TEXT,
            expected_values_future_quarters TEXT,
            risk_assessment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticker) REFERENCES financials(ticker),
            FOREIGN KEY (quarter) REFERENCES quarter(quarter),
            UNIQUE(ticker, quarter, analyst_name)
        )
    ''')
    conn.commit()


def create_table_sentiment_analysis():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quarter TEXT NOT NULL,
            analyst_name TEXT NOT NULL,
            analyst_sentiment TEXT,
            market_sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticker) REFERENCES financials(ticker),
            FOREIGN KEY (quarter) REFERENCES quarter(quarter),
            UNIQUE(ticker, quarter, analyst_name)
        )
    ''')
    conn.commit()


def create_table_leadership_analysis():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leadership_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            quarter TEXT NOT NULL,
            analyst_name TEXT NOT NULL,
            stability_assessment TEXT,
            investor_implications TEXT,
            overall_impact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticker) REFERENCES financials(ticker),
            FOREIGN KEY (quarter) REFERENCES quarter(quarter),
            UNIQUE(ticker, quarter, analyst_name)
        )
    ''')
    conn.commit()


def insert_data(ticker, quarter, metric, value):
    cursor.execute('''
        INSERT INTO financials (ticker, quarter, metric, value)
        VALUES (?, ?, ?, ?)
    ''', (ticker, quarter, metric, value))
    conn.commit()


def get_metric_value(df, metric_name, col):
    """Helper function to get metric value from dataframe"""
    for idx in df.index:
        if idx.strip().lower() == metric_name.lower():
            return df.loc[idx, col]
    return None


def calculate_derived_metrics(ticker, df, dat):
    """Calculate all derived metrics for each quarter"""
    
    # Get dividend data
    dividends = dat.dividends
    
    # Get current price for dividend yield calculation
    hist = dat.history(period="1d")
    current_price = hist['Close'].iloc[-1] if not hist.empty else None
    
    for col in df.columns:
        quarter_str = f"Q{((col.month - 1) // 3) + 1} {col.year}"
        
        base_metrics = ["total revenue", "basic eps", "ebitda", "net income", "basic average shares"]
        
        for metric in base_metrics:
            value = get_metric_value(df, metric, col)
            if value is not None and pd.notna(value):
                insert_data(ticker, quarter_str, metric, value)
        
        # Now calculate derived metrics
        
        # Get base values for calculations
        total_revenue = get_metric_value(df, "total revenue", col)
        ebitda = get_metric_value(df, "ebitda", col)
        net_income = get_metric_value(df, "net income", col)
        gross_profit = get_metric_value(df, "gross profit", col)
        operating_income = get_metric_value(df, "operating income", col)
        
        # Dividend Rate and Dividend Yield
        try:
            # Calculate quarterly dividend from historical dividends
            quarter_num = (col.month - 1) // 3 + 1
            quarter_start = pd.Timestamp(col.year, (quarter_num - 1) * 3 + 1, 1)
            quarter_end = quarter_start + pd.DateOffset(months=3) - pd.DateOffset(days=1)
            
            if not dividends.empty:
                # Convert to timezone-naive for comparison
                dividends_naive = dividends.copy()
                if dividends_naive.index.tz is not None:
                    dividends_naive.index = dividends_naive.index.tz_localize(None)
                
                # Get dividends paid in this quarter
                quarter_dividends = dividends_naive[(dividends_naive.index >= quarter_start) & (dividends_naive.index <= quarter_end)]
                
                if not quarter_dividends.empty:
                    # Sum of dividends in the quarter
                    quarterly_dividend = quarter_dividends.sum()
                    
                    # Store quarterly dividend rate
                    insert_data(ticker, quarter_str, "dividend rate", quarterly_dividend)
                    
                    # Calculate dividend yield based on annualized dividend
                    if current_price is not None and current_price > 0:
                        annualized_dividend = quarterly_dividend * 4
                        dividend_yield = (annualized_dividend / current_price) * 100
                        insert_data(ticker, quarter_str, "dividend yield", dividend_yield)
        except Exception as e:
            print(f"Error calculating dividends for {ticker} {quarter_str}: {e}")
        
        # Revenue Growth
        if total_revenue is not None and pd.notna(total_revenue):
            # Get previous quarter's revenue
            prev_col_idx = df.columns.get_loc(col) + 1  # Note: columns are in reverse chronological order
            if prev_col_idx < len(df.columns):
                prev_col = df.columns[prev_col_idx]
                prev_revenue = get_metric_value(df, "total revenue", prev_col)
                
                if prev_revenue is not None and pd.notna(prev_revenue) and prev_revenue != 0:
                    revenue_growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
                    insert_data(ticker, quarter_str, "revenue growth", revenue_growth)
        
        # EBITDA Margin
        if ebitda is not None and total_revenue is not None:
            if pd.notna(ebitda) and pd.notna(total_revenue) and total_revenue != 0:
                ebitda_margin = (ebitda / total_revenue) * 100
                insert_data(ticker, quarter_str, "ebitda margin", ebitda_margin)
        
        # Profit Margin
        if gross_profit is not None and total_revenue is not None:
            if pd.notna(gross_profit) and pd.notna(total_revenue) and total_revenue != 0:
                profit_margin = (gross_profit / total_revenue) * 100
                insert_data(ticker, quarter_str, "profit margin", profit_margin)
        
        # Operating Margin
        if operating_income is not None and total_revenue is not None:
            if pd.notna(operating_income) and pd.notna(total_revenue) and total_revenue != 0:
                operating_margin = (operating_income / total_revenue) * 100
                insert_data(ticker, quarter_str, "operating margin", operating_margin)


def fill_db(ticker):
    dat = yf.Ticker(ticker)
    df = dat.quarterly_financials
    
    if df.empty:
        print(f"No financial data found for {ticker}.")
        return
    
    # Calculate and insert all metrics
    calculate_derived_metrics(ticker, df, dat)
    
    conn.commit()


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
    create_table_financial_analysis()
    create_table_sentiment_analysis()
    create_table_leadership_analysis()
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        fill_db(ticker)
    
    # Print summary of what was inserted
    cursor.execute('''
        SELECT ticker, metric, COUNT(*) as count
        FROM financials
        GROUP BY ticker, metric
        ORDER BY ticker, metric
    ''')
    
    print("\nSummary of data inserted:")
    for row in cursor.fetchall():
        print(f"{row[0]} - {row[1]}: {row[2]} quarters")
    
    conn.close()


if __name__ == "__main__":
    main()