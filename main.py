import streamlit as st
from src import fileParser
from src import summarizer
from src import anomalyDetection
from dotenv import load_dotenv
import os
from src.updateDb import update_db_from_dict
from src.dbextract import extract_ticker_data, extract_ticker_json
import json

# API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Helper function (for readability)

def Summarizer(data):
    fileParser_output = fileParser.ParseFile(data, api_key).output
    update_db_from_dict(dict(fileParser_output))
    st.write(summarizer.SummarizeFile(data, api_key).output)

def AnomalyDetection(data):
    fileParser_output = fileParser.ParseFile(data, api_key).output
    output = dict(fileParser_output)
    ticker = output["ticker"]
    json = extract_ticker_json(ticker)
    st.write(anomalyDetection.FindAnomaly(json))

def FileParser(data):
    fileParser_output = fileParser.ParseFile(data, api_key).output
    output = dict(fileParser_output)
    ticker = output["ticker"]
    json = extract_ticker_json(ticker)
    st.write(json)
    st.write("testtt")
    update_db_from_dict(output)
    json = extract_ticker_json(ticker)
    st.write(json)
    st.write(fileParser_output)

# Streamlit Interface

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

with col2:
    option = st.radio(
        "Set Usecase",
        ["summarizer", "anomaly-detection", "forecast", "update-database"],
        index=0
    )

if st.button("Submit", type="primary"):
    data = uploaded_file.read()
    if option == "summarizer":
        Summarizer(data)

    elif option == "anomaly-detection":
        AnomalyDetection(data)
    
    elif option == "forecast":
        st.write("forecast")
    
    else: 
        FileParser(data)
