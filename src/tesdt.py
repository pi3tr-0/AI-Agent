import yfinance as yf
import pandas as pd

def get_financial_value(ticker: str, metric: str, year: int):
    """
    Fetches the single value for `metric` in fiscal `year` from yfinance.
    Returns a float (or raises if data is missing).
    """
    tk = yf.Ticker(ticker)
    fin = tk.financials            # DataFrame: index=metrics, columns=datetime
    
    # if yfinance returns an empty DataFrame:
    if fin.empty:
        raise ValueError(f"No financials found for {ticker!r}")
    
    # Convert the column labels (Timestamps) to their years:
    col_years = pd.to_datetime(fin.columns).year
    # Find which column(s) match our target year:
    mask = (col_years == year)
    if not mask.any():
        raise KeyError(f"No data for year {year} in {ticker!r}'s financials")
    
    # There could be multiple columns in the same year; take the last one
    col = fin.columns[mask][-1]
    
    try:
        value = fin.loc[metric, col]
    except KeyError:
        raise KeyError(f"Metric {metric!r} not found in {ticker!r}'s financials")
    
    # If it’s a Pandas scalar (numpy type), cast to float:
    return float(value)

# Example usage:
if __name__ == "__main__":
    ticker = "AAPL"
    metric = "Growth Revenue"
    year = 2021
    val = get_financial_value(ticker, metric, year)
    print(f"{ticker} {metric} in {year} = {val:,}")