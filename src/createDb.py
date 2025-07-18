import yfinance as yf
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "util", "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "finance_relational.db")

# Delete old DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Only include these metrics - separated by type
historical_metrics = [
    "Total Revenue", "Revenue Growth", "EBITDA", "EBITDA Margin", 
    "Operating Margin", "Net Income", "Profit Margin"
]

current_only_metrics = [
    "Shares Outstanding", "Trailing EPS", "Dividends Per Share",
    "Dividend Yield", "Price/Sales Ratio", "Price/Earnings Ratio", 
    "Price/Book Ratio", "EV/EBITDA", "ROA", "ROE"
]

# Combine for backward compatibility
included_metrics = historical_metrics + current_only_metrics

# Tickers to process
tickers = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "NFLX", "ADBE", "INTC"]

def safe_get_value(data, key, default=None):
    """Safely get value from dict/object"""
    try:
        return data.get(key, default) if hasattr(data, 'get') else default
    except:
        return default

def ingest_ticker(symbol, cursor, conn, metric_map, historical_only=False):
    print(f"\n⏳ Processing {symbol}...")
    cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (symbol,))
    conn.commit()
    company_id = cursor.execute("SELECT id FROM companies WHERE ticker = ?", (symbol,)).fetchone()[0]
    tk = yf.Ticker(symbol)
    
    all_data = []
    
    try:
        # 1. Get data from income statement (quarterly and annual)
        print(f"   📊 Fetching income statement data...")
        income_stmt = tk.income_stmt
        
        # Process annual data
        if not income_stmt.empty:
            for col in income_stmt.columns:
                year = pd.to_datetime(col).year
                
                # Total Revenue
                if "Total Revenue" in income_stmt.index:
                    revenue = income_stmt.loc["Total Revenue", col]
                    if pd.notna(revenue):
                        all_data.append({
                            "Metric": "Total Revenue",
                            "Year": year,
                            "Value": float(revenue)
                        })
                
                # Net Income
                if "Net Income" in income_stmt.index:
                    net_income = income_stmt.loc["Net Income", col]
                    if pd.notna(net_income):
                        all_data.append({
                            "Metric": "Net Income",
                            "Year": year,
                            "Value": float(net_income)
                        })
                        
                        # Calculate Profit Margin if we have revenue
                        if "Total Revenue" in income_stmt.index:
                            revenue = income_stmt.loc["Total Revenue", col]
                            if pd.notna(revenue) and revenue > 0:
                                profit_margin = float(net_income) / float(revenue)
                                all_data.append({
                                    "Metric": "Profit Margin",
                                    "Year": year,
                                    "Value": profit_margin
                                })
                
                # EBITDA - try multiple sources
                ebitda = None
                if "EBITDA" in income_stmt.index:
                    ebitda = income_stmt.loc["EBITDA", col]
                else:
                    # Calculate EBITDA from components
                    operating_income = None
                    if "Operating Income" in income_stmt.index:
                        operating_income = income_stmt.loc["Operating Income", col]
                    elif "EBIT" in income_stmt.index:
                        operating_income = income_stmt.loc["EBIT", col]
                    
                    if operating_income and pd.notna(operating_income):
                        depreciation = 0
                        if "Depreciation And Amortization" in income_stmt.index:
                            dep_value = income_stmt.loc["Depreciation And Amortization", col]
                            if pd.notna(dep_value):
                                depreciation = dep_value
                        ebitda = float(operating_income) + float(depreciation)
                
                if ebitda and pd.notna(ebitda):
                    all_data.append({
                        "Metric": "EBITDA",
                        "Year": year,
                        "Value": float(ebitda)
                    })
                    
                    # Calculate EBITDA Margin
                    if "Total Revenue" in income_stmt.index:
                        revenue = income_stmt.loc["Total Revenue", col]
                        if pd.notna(revenue) and revenue > 0:
                            ebitda_margin = float(ebitda) / float(revenue)
                            all_data.append({
                                "Metric": "EBITDA Margin",
                                "Year": year,
                                "Value": ebitda_margin
                            })
                
                # Operating Margin
                if "Operating Income" in income_stmt.index and "Total Revenue" in income_stmt.index:
                    operating_income = income_stmt.loc["Operating Income", col]
                    revenue = income_stmt.loc["Total Revenue", col]
                    if pd.notna(operating_income) and pd.notna(revenue) and revenue > 0:
                        operating_margin = float(operating_income) / float(revenue)
                        all_data.append({
                            "Metric": "Operating Margin",
                            "Year": year,
                            "Value": operating_margin
                        })
        
        # 2. Calculate Revenue Growth from historical data
        revenue_data = [d for d in all_data if d["Metric"] == "Total Revenue"]
        revenue_data.sort(key=lambda x: x["Year"])
        
        for i in range(1, len(revenue_data)):
            curr_year = revenue_data[i]["Year"]
            curr_value = revenue_data[i]["Value"]
            prev_value = revenue_data[i-1]["Value"]
            
            if prev_value > 0:
                growth = (curr_value / prev_value - 1)
                all_data.append({
                    "Metric": "Revenue Growth",
                    "Year": curr_year,
                    "Value": growth
                })
        
        # 3. Only add current metrics if not in historical_only mode
        if not historical_only:
            print(f"   📈 Fetching current metrics...")
            info = tk.info
            current_year = datetime.now().year
            
            # Only add current-only metrics
            metrics_to_fetch = {
                "Shares Outstanding": "sharesOutstanding",
                "Trailing EPS": "trailingEps",
                "Dividends Per Share": "dividendRate",
                "Dividend Yield": "dividendYield",
                "Price/Sales Ratio": "priceToSalesTrailing12Months",
                "Price/Earnings Ratio": "trailingPE",
                "Price/Book Ratio": "priceToBook",
                "ROA": "returnOnAssets",
                "ROE": "returnOnEquity"
            }
            
            for metric_name, info_key in metrics_to_fetch.items():
                value = safe_get_value(info, info_key)
                if value is not None:
                    all_data.append({
                        "Metric": metric_name,
                        "Year": current_year,
                        "Value": float(value)
                    })
            
            # Calculate EV/EBITDA
            enterprise_value = safe_get_value(info, "enterpriseValue")
            ebitda = safe_get_value(info, "ebitda")
            
            if enterprise_value and ebitda and ebitda > 0:
                ev_ebitda = enterprise_value / ebitda
                all_data.append({
                    "Metric": "EV/EBITDA",
                    "Year": current_year,
                    "Value": float(ev_ebitda)
                })
        
        # 4. Deduplicate data before insertion
        # Create a dictionary to store unique metric-year combinations, keeping the first occurrence
        unique_data = {}
        for data_point in all_data:
            if data_point["Metric"] in included_metrics:
                key = (data_point["Metric"], data_point["Year"])
                if key not in unique_data:
                    unique_data[key] = data_point
        
        # Convert back to list
        filtered_data = list(unique_data.values())
        
        print(f"   💾 Saving {len(filtered_data)} unique data points (from {len(all_data)} total)...")
        
        # Insert data into database
        inserted_count = 0
        skipped_count = 0
        for data_point in filtered_data:
            metric_id = metric_map.get(data_point["Metric"])
            if metric_id and pd.notna(data_point["Value"]):
                try:
                    cursor.execute(
                        "INSERT OR REPLACE INTO financials (company_id, metric_id, year, value) VALUES (?, ?, ?, ?)",
                        (company_id, metric_id, int(data_point["Year"]), float(data_point["Value"]))
                    )
                    inserted_count += 1
                except Exception as e:
                    print(f"   ⚠️ Failed to insert {data_point}: {e}")
                    skipped_count += 1
            else:
                skipped_count += 1
        
        conn.commit()
        if skipped_count > 0:
            print(f"   ⚠️ Skipped {skipped_count} duplicate or invalid entries")
        print(f"   ✅ Successfully saved {inserted_count} metrics for {symbol}")
        
    except Exception as e:
        print(f"   ❌ Failed to process {symbol}: {e}")
        import traceback
        traceback.print_exc()

# Init DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.executescript("""
DROP TABLE IF EXISTS financials;
DROP TABLE IF EXISTS metrics;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE
);

CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

CREATE TABLE financials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    metric_id INTEGER,
    year INTEGER,
    value REAL,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (metric_id) REFERENCES metrics(id),
    UNIQUE(company_id, metric_id, year)
);

CREATE INDEX idx_company_metric ON financials(company_id, metric_id);
CREATE INDEX idx_year ON financials(year);
""")

# Seed metrics
for m in included_metrics:
    cursor.execute("INSERT INTO metrics (name) VALUES (?)", (m,))
conn.commit()

# Metric map
metric_map = {name: mid for mid, name in cursor.execute("SELECT id, name FROM metrics")}

# Process tickers
if __name__ == "__main__":
    print(f"Starting data ingestion for {len(tickers)} tickers...")
    print(f"Database path: {DB_PATH}")
    
    # Add option to process with only historical metrics
    import argparse
    parser = argparse.ArgumentParser(description='Ingest financial data into database')
    parser.add_argument('--historical-only', action='store_true', 
                        help='Only collect historical metrics (same metrics for all years)')
    args = parser.parse_args()
    
    for symbol in tickers:
        ingest_ticker(symbol, cursor, conn, metric_map, historical_only=args.historical_only)
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    cursor.execute("""
        SELECT c.ticker, COUNT(DISTINCT f.metric_id) as metric_count, 
               COUNT(DISTINCT f.year) as year_count,
               COUNT(*) as total_records
        FROM companies c
        LEFT JOIN financials f ON c.id = f.company_id
        GROUP BY c.ticker
        ORDER BY c.ticker
    """)
    
    results = cursor.fetchall()
    print(f"\n{'Ticker':<10} {'Metrics':<10} {'Years':<10} {'Total Records':<15}")
    print("-"*45)
    for row in results:
        print(f"{row[0]:<10} {row[1]:<10} {row[2]:<10} {row[3]:<15}")
    
    # Total statistics
    cursor.execute("SELECT COUNT(*) FROM financials")
    total_records = cursor.fetchone()[0]
    print(f"\nTotal records in database: {total_records}")
    
    conn.close()
    print("\n✅ Database creation complete!")