import sqlite3
import os
from src.createdb import ingest_ticker, included_metrics

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "util", "database", "finance_relational.db")

# Helper to normalize metric names
def normalize(name):
    return name.lower().replace(" ", "")

# Main callable function
def update_db_from_dict(data: dict):
    ticker = data.get("ticker", "").upper()
    year = int(data.get("year", 0))
    if not ticker or not year:
        print("❌ Missing ticker or year.")
        return -1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure ticker in companies table
    cursor.execute("INSERT OR IGNORE INTO companies (ticker) VALUES (?)", (ticker,))
    conn.commit()

    # Get company_id
    cursor.execute("SELECT id FROM companies WHERE ticker = ?", (ticker,))
    company_id_row = cursor.fetchone()
    if not company_id_row:
        print(f"❌ Could not find ticker {ticker}")
        conn.close()
        return -2
    company_id = company_id_row[0]

    # Metric normalization map
    metric_map = {}
    for mid, name in cursor.execute("SELECT id, name FROM metrics"):
        normalized = normalize(name)
        metric_map[normalized] = (mid, name)

    # If no data exists yet, ingest full financials from yfinance
    cursor.execute("SELECT 1 FROM financials WHERE company_id = ?", (company_id,))
    has_data = cursor.fetchone()
    if not has_data:
        print(f"🆕 New ticker {ticker} — populating from yfinance")
        ingest_ticker(
            ticker,
            cursor,
            conn,
            {v[1]: v[0] for v in metric_map.values()},
        )

    # Now update based on JSON string
    updates = 0
    for k, v in data.items():
        if k.lower() in ["ticker", "year"]:
            continue

        normalized_key = normalize(k)
        if normalized_key not in metric_map:
            print(f"⚠️ Skipping unknown metric '{k}' — not in DB.")
            continue

        metric_id, canonical_name = metric_map[normalized_key]

        # Check for existing record
        cursor.execute(
            """
            SELECT id FROM financials
            WHERE company_id = ? AND metric_id = ? AND year = ?
            """,
            (company_id, metric_id, year),
        )
        exists = cursor.fetchone()

        if exists:
            if v is not None:
                cursor.execute(
                    "UPDATE financials SET value = ? WHERE id = ?", (v, exists[0])
                )
        else:
            cursor.execute(
                """
                INSERT INTO financials (company_id, metric_id, year, value)
                VALUES (?, ?, ?, ?)
                """,
                (company_id, metric_id, year, v if v is not None else "n/a"),
            )
        updates += 1

    conn.commit()
    conn.close()
    print(f"✅ Updated {ticker} - {year} ({updates} metric(s))")
    return 1


# Optional CLI usage
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python updateDB.py '{\"ticker\": ..., \"year\": ..., ...}'")
    else:
        try:
            json_input = json.loads(sys.argv[1])
            update_db_from_dict(json_input)
        except Exception as e:
            print(f"❌ Invalid JSON string: {e}")