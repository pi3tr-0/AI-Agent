import sqlite3
import json
import os
import re
import sys

# Locate the DB alongside createDb.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "util", "database")
DB_PATH = os.path.join(DB_DIR, "finance_relational.db")


def normalize_metric(name: str) -> str:
    """
    Convert metrics from Title Case to lowerCamelCase, e.g.
    "Total Revenue" -> "totalRevenue"
    """
    parts = re.split(r'[^A-Za-z0-9]+', name)
    parts = [p for p in parts if p]
    if not parts:
        return ""
    first, *rest = parts
    return first.lower() + "".join(p.capitalize() for p in rest)


def check_database():
    """Check if database exists and has data"""
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"DEBUG: Tables in database: {[t[0] for t in tables]}")
    
    # Check record counts
    for table in ['companies', 'metrics', 'financials']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"DEBUG: {table} table has {count} records")
    
    # Check available tickers
    cursor.execute("SELECT ticker FROM companies")
    tickers = cursor.fetchall()
    print(f"DEBUG: Available tickers: {[t[0] for t in tickers]}")
    
    conn.close()
    return True


def extract_ticker_data(ticker: str, debug: bool = False) -> dict:
    """
    Query the database for all metrics of a given ticker,
    returning a dict mapping each year (as string) to a
    dict of lowerCamelCase metric names and their values.
    """
    if debug:
        print(f"\nDEBUG: Extracting data for ticker: {ticker}")
        print(f"DEBUG: Database path: {DB_PATH}")
        
        if not check_database():
            return {}
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return {}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # First check if the ticker exists
    cursor.execute(
        "SELECT id FROM companies WHERE ticker = ?",
        (ticker.upper(),)
    )
    company_result = cursor.fetchone()
    
    if not company_result:
        if debug:
            print(f"DEBUG: Ticker '{ticker}' not found in database")
            # Show available tickers
            cursor.execute("SELECT ticker FROM companies")
            available = [row[0] for row in cursor.fetchall()]
            print(f"DEBUG: Available tickers: {available}")
        conn.close()
        return {}
    
    company_id = company_result[0]
    if debug:
        print(f"DEBUG: Found company_id: {company_id} for ticker: {ticker}")
    
    # Now get the data
    cursor.execute(
        """
        SELECT f.year, m.name, f.value
        FROM financials AS f
        JOIN companies AS c ON f.company_id = c.id
        JOIN metrics   AS m ON f.metric_id = m.id
        WHERE c.ticker = ?
        ORDER BY f.year ASC
        """,
        (ticker.upper(),)
    )
    rows = cursor.fetchall()
    
    if debug:
        print(f"DEBUG: Found {len(rows)} rows of data")
        if rows:
            print(f"DEBUG: Sample row: {rows[0]}")
    
    conn.close()

    data = {}
    for year, metric_name, value in rows:
        year_str = str(year)
        normalized_name = normalize_metric(metric_name)
        
        if debug and len(data) == 0:  # Print first conversion as example
            print(f"DEBUG: Converting '{metric_name}' -> '{normalized_name}'")
        
        data.setdefault(year_str, {})[normalized_name] = value
    
    if debug:
        print(f"DEBUG: Final data structure has {len(data)} years")
        if data:
            first_year = list(data.keys())[0]
            print(f"DEBUG: Metrics for {first_year}: {list(data[first_year].keys())}")
    
    return data


def extract_ticker_json(ticker: str, debug: bool = False) -> str:
    """
    Wrapper to return the extracted data as a JSON-formatted string.
    """
    data = extract_ticker_data(ticker, debug=debug)
    return json.dumps(data, indent=2)


def test_extraction():
    """Test function to verify extraction works"""
    print("=== Testing Database Extraction ===")
    print(f"Database path: {DB_PATH}")
    print(f"Database exists: {os.path.exists(DB_PATH)}")
    
    if os.path.exists(DB_PATH):
        # Test with debug mode
        test_ticker = "AAPL"
        print(f"\nTesting extraction for {test_ticker}:")
        data = extract_ticker_data(test_ticker, debug=True)
        
        if data:
            print(f"\nSuccess! Found data for {len(data)} years")
            print("Sample output:")
            print(json.dumps(data, indent=2)[:500] + "...")
        else:
            print("\nNo data found. Checking database...")
            check_database()


def main():
    if len(sys.argv) == 1:
        # No arguments, run test
        test_extraction()
    elif len(sys.argv) == 2:
        ticker = sys.argv[1]
        if ticker.lower() == "--test":
            test_extraction()
        else:
            print(extract_ticker_json(ticker))
    elif len(sys.argv) == 3 and sys.argv[2] == "--debug":
        ticker = sys.argv[1]
        print(extract_ticker_json(ticker, debug=True))
    else:
        print(f"Usage: {sys.argv[0]} TICKER [--debug]")
        print(f"   or: {sys.argv[0]} --test")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Example usage from another file:
#
# from dbextract import extract_ticker_data
# data = extract_ticker_data('AAPL')
# print(data)
#
# For debugging:
# data = extract_ticker_data('AAPL', debug=True)