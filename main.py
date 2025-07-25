import streamlit as st
from dotenv import load_dotenv
from src import fileParser
from src import internetSearch
import os

# Functions
def ParsePDFAndSearch(pdfBytes, gemini_api_key, tavily_api_key):

    # parse pdf
    fileParserOutput = dict(fileParser.ParseFile(pdfBytes, gemini_api_key).output)
            
    # to access financialMetrics: = dict(fileParserOutput["financialMetrics"])
    # to access pdfSummary: = fileParserOutput["pdfSummary"]
    # to access analyst: = dict(fileParserOutput["analyst"])
    ticker = fileParserOutput["ticker"]
    period = fileParserOutput["period"]

    # search
    searchResult = internetSearch.Search(ticker, period, gemini_api_key, tavily_api_key).output
    fileParserOutput["searchResult"] = searchResult

    return fileParserOutput

# API key
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Streamlit Interface
prompt = st.chat_input(
    "Optional: Additional Query",
    accept_file=True,
    file_type=["pdf"],
)
if prompt:
    if prompt["files"]:
        pdfBytes = prompt["files"][0].read()
        
        content = ParsePDFAndSearch(pdfBytes, gemini_api_key, tavily_api_key)
        
        st.write(content)

    else:
        st.write("PDF Required")
    

