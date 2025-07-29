from src import anomalyDetection, dbextract
import streamlit as st

def main():
    ticker = "NFLX"

    st.write(ticker)

    st.write(anomalyDetection.FindAnomaly(ticker))

    return

if __name__=="__main__":
    main()

