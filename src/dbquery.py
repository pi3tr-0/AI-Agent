import streamlit as st
import sqlite3
import pandas as pd
import os

# Set database path
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 "..", "util", "database", "finance_relational.db")
)

def run_query(query, params=()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"❌ SQL Execution Error: {e}")
        return None

def build_sql_query(ticker, year, metric):
    sql = """
    SELECT c.ticker,
           m.name   AS metric,
           f.year,
           f.value
      FROM financials f
      JOIN companies c ON f.company_id = c.id
      JOIN metrics  m ON f.metric_id   = m.id
     WHERE 1=1
    """
    conditions, params = [], []

    if ticker != "*":
        conditions.append("c.ticker = ?")
        params.append(ticker.upper())

    if year != "*":
        conditions.append("f.year = ?")
        try:
            params.append(int(year))
        except ValueError:
            # leave as string so SQL will error and we catch it
            params.append(year)

    if metric != "*":
        conditions.append("m.name = ?")
        params.append(metric)

    if conditions:
        sql += " AND " + " AND ".join(conditions)

    sql += " ORDER BY c.ticker, f.year, m.name"
    return sql, params

st.title("📊 Financial DB Structured Query")
st.markdown("""
**Enter your query:**  
`Ticker Year Metric`  
Use `*` as a wildcard.  
- `AAPL 2026 Total Revenue`  
- `AAPL 2026 *`  
- `AAPL * *`  
- `* * *`  
""")

user_input = st.text_input("Query (Ticker Year Metric)")

if st.button("Submit"):
    if not user_input:
        st.error("❌ Please enter a query.")
    else:
        parts = user_input.strip().split()
        if len(parts) < 3:
            st.error("❌ Input must have at least 3 parts: Ticker, Year, Metric.")
        else:
            ticker = parts[0]
            year   = parts[1]
            metric = " ".join(parts[2:])  # join the rest for multi-word metrics

            with st.spinner("🔍 Querying database..."):
                sql, params = build_sql_query(ticker, year, metric)
                df = run_query(sql, params)

                if df is None:
                    # run_query already reported the error
                    pass
                elif df.empty:
                    st.error("❌ No data found for that query.")
                else:
                    st.success(f"✅ Found {len(df)} record(s)")
                    st.dataframe(df, use_container_width=True)