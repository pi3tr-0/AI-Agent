import streamlit as st
from dotenv import load_dotenv
from src import fileParser, internetSearch, sentimentAnalysis, financialAnalysis, leadershipSearch, leadershipAnalysis
import os
import asyncio
import nest_asyncio
from typing import Any, Dict

# -------------------------------
# Functions
# -------------------------------
def ParsePDFAndSearch(pdfBytes: bytes, gemini_api_key: str, tavily_api_key: str) -> Dict[str, Any]:
    """
    Parse a PDF file, extract financial data, and perform an internet search for the ticker and period.
    Returns a dictionary with parsed and searched data.
    """
    # Parse the PDF and extract financial metrics and analyst info
    fileParserOutput = dict(fileParser.ParseFile(pdfBytes, gemini_api_key).output)

    # Ensure nested dicts for JSON compatibility
    fileParserOutput["financialMetrics"] = dict(fileParserOutput.get("financialMetrics", {}))
    fileParserOutput["analyst"] = dict(fileParserOutput.get("analyst", {}))

    ticker = fileParserOutput.get("ticker")
    period = fileParserOutput.get("period")

    # Perform internet search if ticker and period are available
    if ticker and period:
        searchResult = internetSearch.Search(ticker, period, gemini_api_key, tavily_api_key).output
        fileParserOutput["searchResult"] = searchResult
    else:
        fileParserOutput["searchResult"] = {}

    # TODO: Update financial metrics database if needed

    return fileParserOutput

## -------------------------------
# Main Streamlit App
## -------------------------------
async def main():
    load_dotenv()  # Load environment variables from .env file
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    st.title("Agentic AI Financial Analyzer")

    # Chat input with PDF upload
    prompt = st.chat_input(
        "Optional: Additional Query",
        accept_file=True,
        file_type=["pdf"],
    )

    # Check for required API keys
    if not gemini_api_key or not tavily_api_key:
        st.error("API keys not found. Please set GEMINI_API_KEY and TAVILY_API_KEY in your .env file.")
        return

    # Handle user input and PDF upload
    if prompt:
        if prompt.get("files"):
            pdfBytes = prompt["files"][0].read()
            # Parse PDF and perform search
            content = ParsePDFAndSearch(pdfBytes, gemini_api_key, tavily_api_key)
            st.write("## Parsed PDF")
            st.write(content)

            ticker = content.get("ticker", "")
            period = content.get("period", "")

            # Run sentiment, financial, and leadership analysis concurrently with error handling
            try:
                sentiment, financial, leadership_search = await asyncio.gather(
                    sentimentAnalysis.AnalyzeSentiment(content, gemini_api_key),
                    financialAnalysis.AnalyzeFinancial(ticker, period, gemini_api_key),
                    leadershipSearch.LeadershipSearch(ticker, period, gemini_api_key),  # Fixed: Added await
                    return_exceptions=True
                )
                
                # Handle sentiment analysis results
                if isinstance(sentiment, Exception):
                    st.error(f"Sentiment Analysis Error: {str(sentiment)}")
                else:
                    st.write("## Sentiment Analysis")
                    st.write(sentiment.output)
                
                # Handle financial analysis results
                if isinstance(financial, Exception):
                    st.error(f"Financial Analysis Error: {str(financial)}")
                else:
                    st.write("## Financial Analysis")
                    st.write(financial.output)
                
                # Handle leadership search results
                if isinstance(leadership_search, Exception):
                    st.error(f"Leadership Search Error: {str(leadership_search)}")
                else:
                    # st.write("## Leadership Search")
                    # st.write(leadership_search)
                    
                    # Run leadership analysis with correct parameters
                    try:
                        # Fixed: Pass ticker and period, not search results
                        leadership_analysis = await leadershipAnalysis.AnalyzeLeadership(ticker, period, gemini_api_key)
                        st.write("## Leadership Analysis")
                        st.write(leadership_analysis.output)
                    except Exception as e:
                        st.error(f"Leadership Analysis Error: {str(e)}")
                    
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")
        else:
            st.warning("PDF Required. Please upload a PDF file.")

## -------------------------------
# Run the Streamlit app
## -------------------------------
if __name__ == "__main__":
    nest_asyncio.apply()  # Allow nested event loops for Streamlit
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())