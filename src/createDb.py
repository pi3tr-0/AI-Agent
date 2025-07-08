import yfinance as yf
import sqlite3
import pandas as pd
import os

# Define paths
BASE_DIR = os.path.dirname("/Users/admin/Desktop/AI-Agent/src")
DB_DIR = os.path.join(BASE_DIR, "..", "util", "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "finance_relational.db")

# Metrics
base_metrics = [
    "Total Revenue", "Net Income", "Diluted EPS", "Gross Profit", "EBITDA", "EBIT",
    "Pretax Income", "Tax Provision", "Research And Development",
    "Selling General And Administration", "Cost Of Revenue", "Total Expenses",
    "Interest Expense", "Normalized Income"
]

derived_metrics = [
    "Revenue Growth", "Operating Margin", "EBITDA Margin", "Net Margin",
    "Shares Outstanding", "Trailing EPS", "Forward EPS", "Dividends Per Share",
    "Dividend Yield", "Price/Sales Ratio", "Price/Earnings Ratio", "Price/Book Ratio",
    "EV/EBITDA", "ROA", "ROE", "Debt/Capital Ratio", "Equity/Assets Ratio",
    "Total Debt/EBITDA", "EBITDA/Interest Expense"
]

all_metrics = base_metrics + derived_metrics

# Tickers to process
tickers = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "NFLX", "ADBE", "INTC"]

def ingest_ticker(symbol, cursor, conn, metric_map, base_metrics):
    print(f"⏳ Processing {symbol}...")
    cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (symbol,))
    conn.commit()
    company_id = cursor.execute("SELECT id FROM companies WHERE ticker = ?", (symbol,)).fetchone()[0]
    tk = yf.Ticker(symbol)

    try:
        available = tk.financials.index.tolist()
        valid_base = [m for m in base_metrics if m in available]
        if not valid_base:
            print(f"⚠️ No base metrics available for {symbol}, skipping.")
            return

        fin = (
            tk.financials
              .loc[valid_base]
              .reset_index()
              .melt(id_vars="index", var_name="Date", value_name="Value")
              .rename(columns={"index": "Metric"})
        )
        fin["Year"] = pd.to_datetime(fin["Date"]).dt.year

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

        info = tk.info
        ebitda = info.get("ebitda")
        debt = info.get("totalDebt")
        eqty = info.get("totalStockholderEquity")
        assets = info.get("totalAssets")
        interest = info.get("interestExpense")

        extra = {
            "Operating Margin": info.get("operatingMargins"),
            "EBITDA Margin": info.get("ebitdaMargins"),
            "Net Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity"),
            "Debt/Capital Ratio": (debt / (debt + eqty)) if debt and eqty else None,
            "Equity/Assets Ratio": (eqty / assets) if eqty and assets else None,
            "Total Debt/EBITDA": (debt / ebitda) if debt and ebitda else None,
            "EBITDA/Interest Expense": (ebitda / interest) if ebitda and interest else None,
            "Shares Outstanding": info.get("sharesOutstanding"),
            "Trailing EPS": info.get("trailingEps"),
            "Forward EPS": info.get("forwardEps"),
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
        full = pd.concat([fin, rev_growth_df, extra_df], ignore_index=True)

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
for m in all_metrics:
    cursor.execute("INSERT INTO metrics (name) VALUES (?)", (m,))
conn.commit()

# Metric map
metric_map = {name: mid for mid, name in cursor.execute("SELECT id, name FROM metrics")}

# Process tickers
if __name__ == "__main__":
    for symbol in tickers:
        ingest_ticker(symbol, cursor, conn, metric_map, base_metrics)
    conn.close()

conn.close()