import streamlit as st
from dotenv import load_dotenv
from src import fileParser
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
            fileParserOutput = dict(fileParser.ParseFile(pdfBytes, api_key).output)
            
            financialMetrics = dict(fileParserOutput["financialMetrics"])
            pdfSummary = fileParserOutput["pdfSummary"]
            analyst = dict(fileParserOutput["analyst"])
            ticker = fileParserOutput["ticker"]

            text = "Amazon's recent moves reflect a dynamic blend of innovation, restructuring, and strategic alignment. The tech giant invested in Lumotive, a startup specializing in programmable optics for autonomous vehicles and data centers, signaling its commitment to next-gen infrastructure. It also acquired Bee, a company behind a $50 AI-powered wristband that transcribes conversations in real time and functions as a personal assistant—potentially adding a new dimension to Amazon's Alexa ecosystem, with strong privacy protections in place. Meanwhile, Amazon Web Services trimmed its workforce by several hundred roles, mainly in senior and specialist teams, as it pivots toward AI-driven operations. On the political front, former CEO Jeff Bezos reportedly met with Donald Trump, potentially clearing the way for renewed support of Bezos's space venture, Blue Origin, in the wake of Elon Musk's waning influence with the administration." # Example internet search result
            fileParserOutput["internetSearch"] = text

            st.write(fileParserOutput)

    else:
        st.write("PDF Required")
    

