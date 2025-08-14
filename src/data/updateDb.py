"""
This script updates a SQLite database with financial data for a specific company.
It takes a dictionary containing financial metrics and inserts them into the database.
"""

import os
import sqlite3
import yfinance as yf
import streamlit as st
from datetime import datetime

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


def update_financial_analysis(ticker, quarter, financial_analysis_data):
    """
    Update financial analysis table with new data
    
    Args:
        ticker: Company ticker symbol
        quarter: Quarter in format 'Q1 2025'
        financial_analysis_data: Dictionary containing:
            - analyst_name: str (REQUIRED - cannot be null)
            - price_target: float
            - analyst_summary: str
            - performance_summary: str
            - investment_outlook: str
            - expected_values_future_quarters: str
            - risk_assessment: str
    """
    # Validate analyst_name is not null
    analyst_name = financial_analysis_data.get('analyst_name')
    if not analyst_name or analyst_name.strip() == '':
        analyst_name = 'Analyst A'  # Default fallback
        financial_analysis_data['analyst_name'] = analyst_name
    
    finance_db = "util/database/finance.db"
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()
    
    # Check if record exists (considering analyst_name as well)
    cursor.execute('''
        SELECT id FROM financial_analysis 
        WHERE ticker = ? AND quarter = ? AND analyst_name = ?
    ''', (ticker, quarter, financial_analysis_data.get('analyst_name')))
    
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Update existing record
        cursor.execute('''
            UPDATE financial_analysis 
            SET price_target = ?, analyst_summary = ?, performance_summary = ?, 
                investment_outlook = ?, expected_values_future_quarters = ?, 
                risk_assessment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE ticker = ? AND quarter = ? AND analyst_name = ?
        ''', (
            financial_analysis_data.get('price_target'),
            financial_analysis_data.get('analyst_summary'),
            financial_analysis_data.get('performance_summary'),
            financial_analysis_data.get('investment_outlook'),
            financial_analysis_data.get('expected_values_future_quarters'),
            financial_analysis_data.get('risk_assessment'),
            ticker, quarter, financial_analysis_data.get('analyst_name')
        ))
    else:
        # Insert new record
        cursor.execute('''
            INSERT INTO financial_analysis 
            (ticker, quarter, analyst_name, price_target, analyst_summary, performance_summary, 
             investment_outlook, expected_values_future_quarters, risk_assessment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker, quarter,
            financial_analysis_data.get('analyst_name'),
            financial_analysis_data.get('price_target'),
            financial_analysis_data.get('analyst_summary'),
            financial_analysis_data.get('performance_summary'),
            financial_analysis_data.get('investment_outlook'),
            financial_analysis_data.get('expected_values_future_quarters'),
            financial_analysis_data.get('risk_assessment')
        ))
    
    conn.commit()
    conn.close()


def update_sentiment_analysis(ticker, quarter, sentiment_data):
    """
    Update sentiment analysis table with new data
    
    Args:
        ticker: Company ticker symbol
        quarter: Quarter in format 'Q1 2025'
        sentiment_data: Dictionary containing:
            - analyst_name: str (REQUIRED - cannot be null)
            - analyst_sentiment: str
            - market_sentiment: str
    """
    # Validate analyst_name is not null
    analyst_name = sentiment_data.get('analyst_name')
    if not analyst_name or analyst_name.strip() == '':
        analyst_name = 'Analyst A'  # Default fallback
        sentiment_data['analyst_name'] = analyst_name
    
    finance_db = "util/database/finance.db"
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()
    
    # Check if record exists (considering analyst_name as well)
    cursor.execute('''
        SELECT id FROM sentiment_analysis 
        WHERE ticker = ? AND quarter = ? AND analyst_name = ?
    ''', (ticker, quarter, sentiment_data.get('analyst_name')))
    
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Update existing record
        cursor.execute('''
            UPDATE sentiment_analysis 
            SET analyst_sentiment = ?, market_sentiment = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE ticker = ? AND quarter = ? AND analyst_name = ?
        ''', (
            sentiment_data.get('analyst_sentiment'),
            sentiment_data.get('market_sentiment'),
            ticker, quarter, sentiment_data.get('analyst_name')
        ))
    else:
        # Insert new record
        cursor.execute('''
            INSERT INTO sentiment_analysis 
            (ticker, quarter, analyst_name, analyst_sentiment, market_sentiment)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            ticker, quarter,
            sentiment_data.get('analyst_name'),
            sentiment_data.get('analyst_sentiment'),
            sentiment_data.get('market_sentiment')
        ))
    
    conn.commit()
    conn.close()


def update_leadership_analysis(ticker, quarter, leadership_data):
    """
    Update leadership analysis table with new data
    
    Args:
        ticker: Company ticker symbol
        quarter: Quarter in format 'Q1 2025'
        leadership_data: Dictionary containing:
            - analyst_name: str (REQUIRED - cannot be null)
            - stability_assessment: str
            - investor_implications: str
            - overall_impact: str
    """
    # Validate analyst_name is not null
    analyst_name = leadership_data.get('analyst_name')
    if not analyst_name or analyst_name.strip() == '':
        analyst_name = 'Analyst A'  # Default fallback
        leadership_data['analyst_name'] = analyst_name
    
    finance_db = "util/database/finance.db"
    conn = sqlite3.connect(finance_db)
    cursor = conn.cursor()
    
    # Check if record exists (considering analyst_name as well)
    cursor.execute('''
        SELECT id FROM leadership_analysis 
        WHERE ticker = ? AND quarter = ? AND analyst_name = ?
    ''', (ticker, quarter, leadership_data.get('analyst_name')))
    
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Update existing record
        cursor.execute('''
            UPDATE leadership_analysis 
            SET stability_assessment = ?, investor_implications = ?, overall_impact = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE ticker = ? AND quarter = ? AND analyst_name = ?
        ''', (
            leadership_data.get('stability_assessment'),
            leadership_data.get('investor_implications'),
            leadership_data.get('overall_impact'),
            ticker, quarter, leadership_data.get('analyst_name')
        ))
    else:
        # Insert new record
        cursor.execute('''
            INSERT INTO leadership_analysis 
            (ticker, quarter, analyst_name, stability_assessment, investor_implications, overall_impact)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            ticker, quarter,
            leadership_data.get('analyst_name'),
            leadership_data.get('stability_assessment'),
            leadership_data.get('investor_implications'),
            leadership_data.get('overall_impact')
        ))
    
    conn.commit()
    conn.close()


def main():
    global conn, cursor
    # update_db_from_dict(expected_output)


if __name__ == "__main__":
    main()