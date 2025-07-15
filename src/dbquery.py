import streamlit as st
import sqlite3
import pandas as pd
import os

# Set database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "util", "database", "finance_relational.db"))
print("USING DB:", DB_PATH)

# Function to run SQL query
def run_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print("❌ SQL Execution Error:", e)
        return None

# Function to build SQL query from structured input
def build_sql_query(ticker, year, metric):
    sql = """
    SELECT c.ticker, m.name AS metric, f.year, f.value
    FROM financials f
    JOIN companies c ON f.company_id = c.id
    JOIN metrics m ON f.metric_id = m.id
    WHERE 1=1
    """
    conditions = []
    params = []

    if ticker != "*":
        conditions.append("c.ticker = ?")
        params.append(ticker.upper())

    if year != "*":
        conditions.append("f.year = ?")
        params.append(int(year))

    if metric != "*":
        conditions.append("m.name = ?")
        params.append(metric)

    if conditions:
        sql += " AND " + " AND ".join(conditions)

    sql += " ORDER BY c.ticker, f.year, m.name"

    return sql, params

# Streamlit UI
st.title("📊 Financial DB Structured Query")

st.markdown("""
Enter your query in the format:  
**`Ticker Year Metric`**  
Use `*` as a wildcard.  
Examples:  
- `AAPL 2026 Total Revenue`  
- `AAPL 2026 *`  
- `AAPL * *`  
- `* * *`  
""")

user_input = st.text_input("Enter Query (Ticker Year Metric):")

if st.button("Submit"):
    try:
        ticker, year, metric = user_input.strip().split()
    except ValueError:
        st.error("❌ Input must be exactly 3 parts: Ticker Year Metric.")
    else:
        with st.spinner("🔍 Querying database..."):
            sql, params = build_sql_query(ticker, year, metric)
            result = run_query(sql, params)
            if result is None or result.empty:
                st.error("❌ No data found for that query.")
            else:
                st.success(f"✅ Found {len(result)} record(s)")
                st.dataframe(result)