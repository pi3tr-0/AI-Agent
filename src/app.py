import streamlit as st
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load prompt template
with open("prompt.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

# Database path
DB_PATH = "finance_relational.db"

def get_available_companies():
    """Return sorted list of tickers."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT ticker FROM companies ORDER BY ticker").fetchall()
    return [r[0] for r in rows]

def get_company_data(ticker):
    """Return DataFrame of year, metric name, value for the given ticker."""
    query = """
    SELECT f.year,
           m.name AS name,
           f.value
    FROM financials AS f
    JOIN companies AS c ON f.company_id = c.id
    JOIN metrics   AS m ON f.metric_id = m.id
    WHERE c.ticker = ?
    ORDER BY f.year, m.name;
    """
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=(ticker,))

def get_metrics_for_company(ticker):
    """Return sorted list of available metrics for the given ticker."""
    query = """
    SELECT DISTINCT m.name
    FROM financials AS f
    JOIN companies AS c ON f.company_id = c.id
    JOIN metrics   AS m ON f.metric_id = m.id
    WHERE c.ticker = ?
    ORDER BY m.name;
    """
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(query, (ticker,)).fetchall()
    return [r[0] for r in rows]

def generate_financial_summary(df, metrics):
    """Compute YoY % changes for selected metrics."""
    years = sorted(df["year"].unique())
    if len(years) < 2:
        return "Not enough years of data to compute changes."
    latest, prev = years[-1], years[-2]

    summary_lines = []
    for metric in metrics:
        vals = df[df["name"] == metric].set_index("year")["value"]
        if latest in vals.index and prev in vals.index:
            curr, old = vals.loc[latest], vals.loc[prev]
            if pd.notna(curr) and pd.notna(old) and old != 0:
                pct = (curr - old) / old * 100
                summary_lines.append(f"{metric}: {pct:.1f}% change from {prev} to {latest}")
    return "\n".join(summary_lines) if summary_lines else "No valid comparisons for selected metrics."

# --- Streamlit UI ---

st.title("📈 Company Financial Summary")

# 1) Company selector
company_list = get_available_companies()
selected_company = st.selectbox("Choose a company ticker:", company_list)

if selected_company:
    df = get_company_data(selected_company)
    if df.empty:
        st.warning("No data available for this company.")
    else:
        # 2) Metric multi-select
        all_metrics = get_metrics_for_company(selected_company)
        defaults = ["Total Revenue", "Net Income", "EBITDA", "Operating Income", "Diluted EPS"]
        chosen = st.multiselect("Select metrics to analyze:", all_metrics, default=defaults)

        # 3) Show raw data
        st.subheader("Historical Values")
        pivot = df.pivot(index="year", columns="name", values="value")
        st.dataframe(pivot)

        # 4) Show YoY changes
        st.subheader("Year-over-Year % Changes")
        yoy = generate_financial_summary(df, chosen)
        st.code(yoy)

        # 5) LLM analysis
        st.markdown("🧠 **LLM Analysis**")
        if st.button("Analyze with GPT-4"):
            with st.spinner("Analyzing with GPT-4..."):
                response = client.responses.create(
                    model="gpt-4.1",
                    instructions=instructions,
                    input=yoy
                )
            st.success("Analysis complete.")
            st.write(response.output_text)