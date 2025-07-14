import streamlit as st
from src import fileParser
from src import summarizer
from dotenv import load_dotenv
import os

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
        
        #string output in JSON
        json = fileParser_output.model_dump_json()

        #TODO: updateDb function if requirements met

        st.write(summarizer.SummarizeFile(data, api_key).output)

    elif option == "anomaly-detection":
        st.write("anomaly-detection")
    elif option == "forecast":
        st.write("forecast")
    else: 
        fileParser_output = fileParser.ParseFile(data, api_key).output

        #string output in JSON
        #json = fileParser_output.model_dump_json()

        st.write(fileParser_output)
        
        #TODO: updateDb function
        #test