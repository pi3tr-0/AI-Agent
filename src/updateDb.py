import json
import sqlite3
import os
from createDb import ingest_ticker, base_metrics

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "util", "database", "finance_relational.db")

def normalize(name):
    return name.lower().replace(" ", "")

def update_db_from_json(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    ticker = data["ticker"].upper()
    year = int(data["year"])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (ticker,))
    conn.commit()

    cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker,))
    company_id_row = cursor.fetchone()
    if not company_id_row:
        print(f"❌ Could not find ticker {ticker}")
        return
    company_id = company_id_row[0]

    # Create normalized map: "totalrevenue" → (metric_id, "Total Revenue")
    metric_map = {}
    for mid, name in cursor.execute("SELECT id, name FROM metrics"):
        normalized = normalize(name)
        metric_map[normalized] = (mid, name)

    # Check if ticker has existing data
    cursor.execute("SELECT 1 FROM financials WHERE company_id = ?", (company_id,))
    has_data = cursor.fetchone()
    if not has_data:
        print(f"🆕 New ticker {ticker} — populating full data from yfinance")
        ingest_ticker(ticker, cursor, conn, {v[1]: v[0] for v in metric_map.values()}, base_metrics)

    for k, v in data.items():
        if k in ["ticker", "year"]:
            continue
        normalized_key = k.lower()
        if normalized_key not in metric_map:
            print(f"⚠️ Skipping unknown metric '{k}' — not found in DB.")
            continue

        metric_id, canonical_name = metric_map[normalized_key]

        # Check if row already exists
        cursor.execute("""
            SELECT id FROM financials
            WHERE company_id = ? AND metric_id = ? AND year = ?
        """, (company_id, metric_id, year))
        exists = cursor.fetchone()

        if exists:
            if v is not None:
                cursor.execute("UPDATE financials SET value = ? WHERE id = ?", (v, exists[0]))
        else:
            cursor.execute("""
                INSERT INTO financials (company_id, metric_id, year, value)
                VALUES (?, ?, ?, ?)
            """, (company_id, metric_id, year, v if v is not None else "n/a"))

    conn.commit()
    conn.close()
    print(f"✅ Updated {ticker} - {year}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python updateDB.py path/to/data.json")
    else:
        update_db_from_json(sys.argv[1])