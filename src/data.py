import yfinance as yf
import sqlite3
import pandas as pd

tickers = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "NFLX", "ADBE", "INTC"]

important_metrics = [
    "Total Revenue",
    "Net Income",
    "Diluted EPS",
    "Gross Profit",
    "Operating Income",
    "EBITDA",
    "EBIT",
    "Pretax Income",
    "Tax Provision",
    "Research And Development",
    "Selling General And Administration",
    "Cost Of Revenue",
    "Total Expenses",
    "Interest Expense",
    "Normalized Income"
]

# Connect to database
conn = sqlite3.connect("finance_relational.db")
cursor = conn.cursor()

# Drop existing tables
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
    FOREIGN KEY (metric_id) REFERENCES metrics(id)
);
""")

# Preload metrics table
for metric in important_metrics:
    cursor.execute("INSERT INTO metrics (name) VALUES (?)", (metric,))

conn.commit()

# Map metric names to IDs
metric_map = {row[1]: row[0] for row in cursor.execute("SELECT * FROM metrics").fetchall()}

# Loop through tickers
for ticker_symbol in tickers:
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.financials
        df = df.loc[df.index.intersection(important_metrics)]
        df = df.reset_index().melt(id_vars="index", var_name="Date", value_name="Value")
        df.columns = ["Metric", "Date", "Value"]
        df["Year"] = pd.to_datetime(df["Date"]).dt.year

        # Insert company
        cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (ticker_symbol,))
        conn.commit()
        cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker_symbol,))
        company_id = cursor.fetchone()[0]

        # Insert financials
        for _, row in df.iterrows():
            metric_id = metric_map.get(row["Metric"])
            if metric_id and not pd.isna(row["Value"]):
                cursor.execute("""
                    INSERT INTO financials (company_id, metric_id, year, value)
                    VALUES (?, ?, ?, ?)
                """, (company_id, metric_id, int(row["Year"]), float(row["Value"])))
        conn.commit()
        print(f"Saved {ticker_symbol}")
    except Exception as e:
        print(f"Failed to process {ticker_symbol}: {e}")

conn.close()