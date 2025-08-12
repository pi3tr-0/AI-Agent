import streamlit as st
from dotenv import load_dotenv
from src import fileParser, internetSearch, sentimentAnalysis, financialAnalysis, leadershipSearch, leadershipAnalysis
from src.updateDb import update_financial_analysis, update_sentiment_analysis, update_leadership_analysis
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

    # Database will be updated after analysis is complete

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
            filename = prompt["files"][0].name
            
            # Extract analyst name from filename: <analyst name> - <ticker> <quarter> <year>
            analyst_name = "Analyst A"  # Default fallback
            try:
                # Split by " - " to get analyst name and rest
                if " - " in filename:
                    analyst_name = filename.split(" - ")[0].strip()
                    # Remove file extension if present
                    if "." in analyst_name:
                        analyst_name = analyst_name.rsplit(".", 1)[0]
            except Exception as e:
                st.warning(f"Could not extract analyst name from filename: {e}")
            
            # Parse PDF and perform search
            content = ParsePDFAndSearch(pdfBytes, gemini_api_key, tavily_api_key)
            
            # Display basic information in a structured format
            ticker = content.get("ticker", "")
            period = content.get("period", "")
            # Use analyst name from filename instead of fileParser
            
            # Create a structured display for basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ticker", ticker)
            with col2:
                st.metric("Period", period)
            with col3:
                st.metric("Analyst", analyst_name)
            
            # Display the full parsed content
            st.write("## Full Parsed Content")
            st.write(content)

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
                        
                        # Update database with analysis results
                        try:
                            # Update financial analysis
                            if not isinstance(financial, Exception):
                                # Extract risk assessment from financial analysis
                                risk_assessment = "Based on financial analysis"
                                if hasattr(financial.output, 'risk_assessment'):
                                    if hasattr(financial.output.risk_assessment, 'risk_level'):
                                        risk_assessment = f"Risk Level: {financial.output.risk_assessment.risk_level}"
                                    elif hasattr(financial.output.risk_assessment, 'key_risks'):
                                        risk_assessment = f"Key Risks: {', '.join(financial.output.risk_assessment.key_risks[:3])}"
                                
                                # Use analyst name extracted from filename
                                # analyst_name is already extracted above from filename
                                
                                financial_data = {
                                    'analyst_name': analyst_name,
                                    'price_target': None,  # Extract from financial.output if available
                                    'analyst_summary': getattr(financial.output, 'performance_summary', 'Analysis completed'),
                                    'performance_summary': getattr(financial.output, 'performance_summary', 'Performance analyzed'),
                                    'investment_outlook': getattr(financial.output, 'investment_outlook', 'Hold'),
                                    'expected_values_future_quarters': 'To be calculated based on analysis',
                                    'risk_assessment': risk_assessment
                                }
                                update_financial_analysis(ticker, period, financial_data)
                            
                            # Update sentiment analysis
                            if not isinstance(sentiment, Exception):
                                sentiment_data = {
                                    'analyst_name': analyst_name,
                                    'analyst_sentiment': getattr(sentiment.output.analyst_sentiment, 'sentiment', 'Neutral') if hasattr(sentiment.output, 'analyst_sentiment') else 'Neutral',
                                    'market_sentiment': getattr(sentiment.output.market_sentiment, 'sentiment', 'Neutral') if hasattr(sentiment.output, 'market_sentiment') else 'Neutral'
                                }
                                update_sentiment_analysis(ticker, period, sentiment_data)
                            
                            # Update leadership analysis
                            if not isinstance(leadership_analysis, Exception):
                                leadership_data = {
                                    'analyst_name': analyst_name,
                                    'stability_assessment': str(getattr(leadership_analysis.output.stability_assessment, 'stability_score', 'Stable')) if hasattr(leadership_analysis.output, 'stability_assessment') else 'Stable',
                                    'investor_implications': getattr(leadership_analysis.output, 'investor_implications', 'Positive implications'),
                                    'overall_impact': getattr(leadership_analysis.output, 'overall_impact', 'Positive')
                                }
                                update_leadership_analysis(ticker, period, leadership_data)
                                
                        except Exception as db_error:
                            st.error(f"Database Update Error: {str(db_error)}")
                            
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