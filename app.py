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

# Connect to the relational database
DB_PATH = "finance_relational.db"

def get_available_companies():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM companies ORDER BY ticker")
    companies = [row[0] for row in cursor.fetchall()]
    conn.close()
    return companies

def get_summary_for_company(ticker):
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT year, metric.name, financials.value
    FROM financials
    JOIN companies ON companies.id = financials.company_id
    JOIN metrics AS metric ON metric.id = financials.metric_id
    WHERE companies.ticker = ?
    ORDER BY year ASC;
    """
    df = pd.read_sql_query(query, conn, params=(ticker,))
    conn.close()
    return df

def generate_financial_summary(df):
    # Create summary string from trends
    summary = ""
    latest_year = df["year"].max()
    prev_year = latest_year - 1

    focus_metrics = ["Total Revenue", "Net Income", "Diluted EPS", "Operating Income", "EBITDA"]
    for metric in focus_metrics:
        yearly = df[df["name"] == metric].set_index("year").sort_index()
        if latest_year in yearly.index and prev_year in yearly.index:
            curr = yearly.loc[latest_year, "value"]
            prev = yearly.loc[prev_year, "value"]
            if pd.notna(curr) and pd.notna(prev) and prev != 0:
                change = (curr - prev) / prev * 100
                summary += f"{metric} changed by {change:.1f}% from {prev_year} to {latest_year}.\n"
    
    return summary

# --- Streamlit UI ---

st.title("📈 Company Financial Summary")

company_options = get_available_companies()
selected_company = st.selectbox("Choose a company ticker:", company_options)

if st.button("Generate Summary"):
    df = get_summary_for_company(selected_company)

    if df.empty:
        st.warning("No data available for this company.")
    else:
        user_summary = generate_financial_summary(df)
        st.text("📋 Summary of raw financial trends:")
        st.code(user_summary)

        st.markdown("🧠 **LLM Analysis**")
        with st.spinner("Analyzing with GPT-4..."):
            response = client.responses.create(
                model="gpt-4.1",
                instructions=instructions,
                input=user_summary
            )
            st.success("Analysis complete.")
            st.write(response.output_text)