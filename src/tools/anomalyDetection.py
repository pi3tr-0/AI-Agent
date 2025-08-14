import pandas as pd
import numpy as np
from src.data import dbextract
from sklearn.linear_model import LinearRegression
from pydantic_ai import Tool

# -------------------------------
# Main Function
# -------------------------------
def FindAnomaly(ticker: str, period: str) -> dict:
    data = dbextract.extract_ticker_data(ticker, period)
    
    # Handle case where no data is available
    if not data:
        return {
            "error": f"No financial data available for ticker {ticker} and period {period}. Please ensure the period is in the format 'Q<1-4> YYYY' (e.g., 'Q3 2024')."
        }
    
    # Map quarter strings to float values for sorting
    quarter_map = {'Q1': 0.0, 'Q2': 0.25, 'Q3': 0.5, 'Q4': 0.75}
    quarter_data = {}
    for key in data:
        quarter, year = key.split()
        num = float(year) + quarter_map.get(quarter, 0.0)
        quarter_data[num] = data[key]

    # Check if we have enough data for analysis
    if len(quarter_data) < 2:
        return {
            "error": f"Insufficient historical data for {ticker}. Need at least 2 quarters of data for anomaly detection."
        }

    # Sort by year+quarter
    sorted_quarters = sorted(quarter_data.items())
    current_quarter = float(sorted_quarters[-1][0])
    current_metrics = sorted_quarters[-1][1]
    past_quarters = dict(sorted_quarters[:-1])

    result = {}
    # Simple Average Comparison
    historical_averages = ComputeSimpleAverages(past_quarters)
    result["simpleAverages"] = CompareSimpleAverages(current_metrics, historical_averages)
    # Linear Regression Comparison
    result["linearRegression"] = CompareLinearRegression(current_quarter, current_metrics, past_quarters)

    df = pd.DataFrame(result).T
    return df.to_dict()


# -------------------------------
# Helper Functions
# -------------------------------
def ComputeLRPredictedValue(currentQuarter, currentQuarterValue, metricDict):
    """
    Predict the expected value for the current quarter using linear regression on historical data.
    Returns a qualitative assessment based on deviation from the predicted value.
    """
    threshold = 0.1  # Threshold for significant change
    quarters = np.array(list(metricDict.keys())).reshape(-1, 1)
    values = np.array(list(metricDict.values()))
    model = LinearRegression()
    model.fit(quarters, values)
    # Require at least some fit quality (R^2 > 0.7)
    if model.score(quarters, values) < 0.7:
        return "Model not valid"
    predicted = model.predict(np.array([[currentQuarter]]))[0]
    diff_ratio = (currentQuarterValue - predicted) / abs(predicted)
    if diff_ratio > threshold:
        return "Higher than expected"
    elif diff_ratio < -threshold:
        return "Lower than expected"
    return "Changes within the tolerable range"

def CompareLinearRegression(currentQuarter, currentQuarterDict, pastQuartersDict):
    """
    Compare current quarter metrics to historical trends using linear regression.
    Returns a dictionary of qualitative assessments for each metric.
    """
    metric_history = {key: {} for key in currentQuarterDict}
    # Build historical data for each metric
    for quarter, metrics in pastQuartersDict.items():
        for key, value in metrics.items():
            if key in metric_history:
                metric_history[key][float(quarter)] = value
    result = {}
    for key, history in metric_history.items():
        if not history:
            result[key] = "No Historical Data"
        else:
            result[key] = ComputeLRPredictedValue(currentQuarter, currentQuarterDict[key], history)
    return result

def ComputeSimpleAverages(pastQuartersDict):
    """
    Compute the average value for each metric across all past quarters.
    Returns a dictionary of averages.
    """
    sums = {}
    counts = {}
    for metrics in pastQuartersDict.values():
        for metric, value in metrics.items():
            sums[metric] = sums.get(metric, 0) + value
            counts[metric] = counts.get(metric, 0) + 1
    averages = {metric: sums[metric] / counts[metric] for metric in sums}
    return averages

def CompareSimpleAverages(currentQuarter, historicalSimpleAverages):
    """
    Compare current quarter metrics to historical averages.
    Returns a dictionary of qualitative assessments for each metric.
    """
    threshold = 0.1  # Threshold for significant change
    changes = {}
    for key, value in currentQuarter.items():
        if key not in historicalSimpleAverages:
            changes[key] = "No historical data"
            continue
        diff_ratio = (value - historicalSimpleAverages[key]) / abs(historicalSimpleAverages[key])
        if diff_ratio > threshold:
            changes[key] = "Higher than expected"
        elif diff_ratio < -threshold:
            changes[key] = "Lower than expected"
        else:
            changes[key] = "Changes within the tolerable range"
    return changes


# -------------------------------
# Tool Declaration
# -------------------------------
AnomalyDetection = Tool(
        FindAnomaly,
        name="anomalyDetection",
        description="Detects financial anomalies using simple average and regression trend analysis. REQUIRES both ticker (e.g., 'AAPL') and period (e.g., 'Q3 2024') parameters.",
    )