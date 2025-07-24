import streamlit as st
from dotenv import load_dotenv
from src import summarizer
import os

# API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Streamlit Interface

prompt = st.chat_input(
    "Optional: Additional Query",
    accept_file=True,
    file_type=["pdf"],
)
if prompt:
    if prompt["files"]:
        pdfBytes = prompt["files"][0].read()
        if prompt.text:
            st.write("PDF and Text")
        else:
            st.write("PDF only")
    else:
        st.write("PDF Required")
    

