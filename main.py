import streamlit as st
from pypdf import PdfReader
from src import fileParser
import io

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

with col2:
    st.radio(
        "Set Usecase",
        ["summarizer", "anomaly-detection", "forecast"],
    )

if st.button("Submit", type="primary"):
    st.write(fileParser.parseFile(uploaded_file))