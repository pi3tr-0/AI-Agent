import streamlit as st
from pypdf import PdfReader

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")

with col2:
    st.radio(
        "Set Usecase",
        ["summarizer", "anomaly-detection", "forecast"],
    )

if st.button("Submit", type="primary"):
    reader = PdfReader(uploaded_file)
    page = reader.pages[0]
    st.write(page.extract_text())