import streamlit as st
from src import fileParser
from src import summarizer
from dotenv import load_dotenv
import os
from src.updatedb import update_db_from_dict
import json

load_dotenv()  # Load variables from .env file
api_key = os.getenv("GEMINI_API_KEY") # Access the variable

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
        st.write("anomaly-detection")
    
    elif option == "forecast":
        st.write("forecast")

    else: 
        fileParser_output = fileParser.ParseFile(data, api_key).output

        json = json.loads(fileParser_output)
        # json = {"year": 2026, "ticker": "AAPL", "ebitda": 1000, "totalrevenue": 5000}
        if update_db_from_dict(json) == 1:
            st.success("Database updated successfully.")
        elif update_db_from_dict(json) == -1:
            st.error("Failed to update database, Missing ticker or year.")
        elif update_db_from_dict(json) == -2:
            st.error("Failed to update database, Could not find ticker.")
        else:
            st.error("Failed to update database, Unknown error.")
        
        #TODO: updateDb function