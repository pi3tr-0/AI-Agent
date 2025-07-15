import yfinance as yf
import sqlite3
import pandas as pd
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "util", "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "finance_relational.db")

# Delete old DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Only include these metrics
included_metrics = [
    "Total Revenue", "Revenue Growth", "EBITDA", "EBITDA Margin", "Operating Margin",
    "Net Income", "Profit Margin", "Shares Outstanding", "Trailing EPS", "Dividends Per Share",
    "Dividend Yield", "Price/Sales Ratio", "Price/Earnings Ratio", "Price/Book Ratio",
    "EV/EBITDA", "ROA", "ROE"
]

# Tickers to process
tickers = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "NFLX", "ADBE", "INTC"]

def ingest_ticker(symbol, cursor, conn, metric_map):
    print(f"⏳ Processing {symbol}...")
    cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (symbol,))
    conn.commit()
    company_id = cursor.execute("SELECT id FROM companies WHERE ticker = ?", (symbol,)).fetchone()[0]
    tk = yf.Ticker(symbol)

    try:
        available = tk.financials.index.tolist()
        valid_base = [m for m in ["Total Revenue", "Net Income", "EBITDA"] if m in available]

        fin = (
            tk.financials
              .loc[valid_base]
              .reset_index()
              .melt(id_vars="index", var_name="Date", value_name="Value")
              .rename(columns={"index": "Metric"})
        )
        fin["Year"] = pd.to_datetime(fin["Date"]).dt.year

        # Revenue Growth
        rev = fin[fin.Metric == "Total Revenue"].sort_values("Year")[["Year", "Value"]].dropna().reset_index(drop=True)
        growth_rows = []
        for i in range(1, len(rev)):
            y, v, prev_v = rev.loc[i, "Year"], rev.loc[i, "Value"], rev.loc[i - 1, "Value"]
            growth_rows.append({
                "Metric": "Revenue Growth",
                "Date": f"{y}-01-01",
                "Value": (v / prev_v - 1),
                "Year": y
            })
        rev_growth_df = pd.DataFrame(growth_rows)

        # Extra ratios from info
        info = tk.info
        ebitda = info.get("ebitda")
        debt = info.get("totalDebt")
        eqty = info.get("totalStockholderEquity")
        assets = info.get("totalAssets")
        interest = info.get("interestExpense")

        extra = {
            "Operating Margin": info.get("operatingMargins"),
            "EBITDA Margin": info.get("ebitdaMargins"),
            "Profit Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity"),
            "Shares Outstanding": info.get("sharesOutstanding"),
            "Trailing EPS": info.get("trailingEps"),
            "Dividends Per Share": info.get("dividendRate"),
            "Dividend Yield": info.get("dividendYield"),
            "Price/Sales Ratio": info.get("priceToSalesTrailing12Months"),
            "Price/Earnings Ratio": info.get("trailingPE"),
            "Price/Book Ratio": info.get("priceToBook"),
            "EV/EBITDA": (info.get("enterpriseValue") / ebitda) if info.get("enterpriseValue") and ebitda else None,
        }

        this_year = pd.Timestamp.now().year
        extra_rows = [
            {"Metric": m, "Date": f"{this_year}-01-01", "Value": v, "Year": this_year}
            for m, v in extra.items() if v is not None
        ]
        extra_df = pd.DataFrame(extra_rows)

        # Combine all
        full = pd.concat([fin, rev_growth_df, extra_df], ignore_index=True)

        # Filter to only included metrics
        full = full[full["Metric"].isin(included_metrics)]

        for _, row in full.iterrows():
            mid = metric_map.get(row["Metric"])
            if mid and pd.notna(row["Value"]):
                cursor.execute(
                    "INSERT INTO financials (company_id, metric_id, year, value) VALUES (?, ?, ?, ?)",
                    (company_id, mid, int(row["Year"]), float(row["Value"]))
                )
        conn.commit()
        print(f"✅ Saved {symbol}")
    except Exception as e:
        print(f"⚠️ Failed {symbol}: {e}")

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
    FOREIGN KEY (metric_id) REFERENCES metrics(id)
);
""")

# Seed metrics
for m in included_metrics:
    cursor.execute("INSERT INTO metrics (name) VALUES (?)", (m,))
conn.commit()

# Metric map
metric_map = {name: mid for mid, name in cursor.execute("SELECT id, name FROM metrics")}

# Process tickers
if __name__ == "__main__":
    for symbol in tickers:
        ingest_ticker(symbol, cursor, conn, metric_map)
    conn.close()