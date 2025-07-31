import streamlit as st
from dotenv import load_dotenv
from src import fileParser, internetSearch, sentimentAnalysis, financialAnalysis
import os
from typing import Any, Dict

# -------------------------------
# Functions
# -------------------------------
def ParsePDFAndSearch(pdfBytes: bytes, gemini_api_key: str, tavily_api_key: str) -> Dict[str, Any]:
    """Parse PDF and perform internet search."""
    fileParserOutput = dict(fileParser.ParseFile(pdfBytes, gemini_api_key).output)
    
    # Required for JSON compatibility
    fileParserOutput["financialMetrics"] = dict(fileParserOutput.get("financialMetrics", {}))
    fileParserOutput["analyst"] = dict(fileParserOutput.get("analyst", {}))

    ticker = fileParserOutput.get("ticker")
    period = fileParserOutput.get("period")

    if ticker and period:
        searchResult = internetSearch.Search(ticker, period, gemini_api_key, tavily_api_key).output
        fileParserOutput["searchResult"] = searchResult
    else:
        fileParserOutput["searchResult"] = {}

    # TODO: Update financial metrics database if needed

    return fileParserOutput

def main():
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    st.title("Agentic AI Financial Analyzer")

    prompt = st.chat_input(
        "Optional: Additional Query",
        accept_file=True,
        file_type=["pdf"],
    )

    if not gemini_api_key or not tavily_api_key:
        st.error("API keys not found. Please set GEMINI_API_KEY and TAVILY_API_KEY in your .env file.")
        return

    if prompt:
        if prompt.get("files"):
            pdfBytes = prompt["files"][0].read()
            content = ParsePDFAndSearch(pdfBytes, gemini_api_key, tavily_api_key)
            st.write(content)

            sentiment = dict(sentimentAnalysis.AnalyzeSentiment(content, gemini_api_key).output)
            st.write(sentiment)

            financial_result = financialAnalysis.AnalyzeFinancial(content.get("ticker", ""), gemini_api_key).output
            st.write(financial_result)
        else:
            st.warning("PDF Required")

if __name__ == "__main__":
    main()

