import streamlit as st
from src import fileParser
from src import summarizer
from src import anomalyDetection
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

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
        fileParser_output = fileParser.ParseFile(data, api_key).output

        #TODO: updateDb function if requirements met

        st.write(summarizer.SummarizeFile(data, api_key).output)

    elif option == "anomaly-detection":
        sampleJSON =  """
                {"2019" : { "revenueGrowth": 0.1, "operatingMargin": -0.1 },
                "2020" : { "revenueGrowth": 0.2, "operatingMargin": -0.2 },
                "2021" : { "revenueGrowth": 0.3, "operatingMargin": -0.3 },
                "2022" : { "revenueGrowth": 0.4, "operatingMargin": -0.4 },
                "2023" : { "revenueGrowth": 0.45, "operatingMargin": -1, "ebitda": 0 }}
                """
        st.write(sampleJSON)
        st.write(anomalyDetection.FindAnomaly(sampleJSON))
    
    elif option == "forecast":
        st.write("forecast")
    
    else: 
        fileParser_output = fileParser.ParseFile(data, api_key).output
        st.write(fileParser_output)
        
        #TODO: updateDb function
        #test