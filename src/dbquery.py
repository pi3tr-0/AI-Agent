import streamlit as st
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "util", "database", "finance_relational.db"))
print("USING DB:", DB_PATH)

# Setup Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = """
You are an expert data analyst. Your job is to write SQLite SQL queries from user questions.

Database schema:
- companies(id INTEGER, ticker TEXT)
- metrics(id INTEGER, name TEXT)
- financials(id INTEGER, company_id INTEGER, metric_id INTEGER, year INTEGER, value REAL)

Always join the necessary tables to return company name, metric name, year, and value.

Here’s an example:

Question: what is apple's net income in 2023?

SQL:
```
SELECT c.ticker, m.name, f.year, f.value
FROM financials f
JOIN companies c ON f.company_id = c.id
JOIN metrics m ON f.metric_id = m.id
WHERE c.ticker = 'AAPL' AND m.name = 'Net Income' AND f.year = 2023
```

Question: give me apple's full financial statement from 2023

SQL:
```
SELECT m.name, f.value
FROM financials f
JOIN companies c ON f.company_id = c.id
JOIN metrics m ON f.metric_id = m.id
WHERE c.ticker = 'AAPL' AND f.year = 2023
```

Now answer this:
"""

def generate_sql(question):
    prompt = f"{SYSTEM_PROMPT}\nUser Question: {question}\n\nSQL:"
    response = model.generate_content(prompt)
    if not response.text:
        return None
    if "```" in response.text:
        return response.text.split("```")[1].strip().lstrip("sql").strip()

def run_query(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print("❌ SQL Execution Error:", e)
        return None

st.title("📊 Financial DB Query Assistant")
user_question = st.text_input("Ask a question about the financial database:")

if st.button("Submit"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("🔍 Thinking..."):
            sql = generate_sql(user_question)
            if sql:
                result = run_query(sql)
                if result is None or result.empty:
                    st.error("❌ Data not available.")
                else:
                    st.success("✅ Result found.")
                    try:
                        if {"ticker", "name", "year", "value"}.issubset(result.columns):
                            row = result.iloc[0]
                            st.markdown(
                                f"📈 **{row['ticker']} | {row['name']} | {row['year']}**: "
                                f"`{float(row['value']):,.0f}`"
                            )
                        else:
                            st.dataframe(result)
                    except Exception:
                        st.warning("Could not format nicely. Showing raw results:")
                        st.dataframe(result)
            else:
                st.error("⚠️ Failed to generate query.")