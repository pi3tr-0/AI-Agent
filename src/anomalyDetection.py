import pandas as pd
import numpy as np
from src import dbextract
from sklearn.linear_model import LinearRegression
from pydantic_ai import Tool

# -------------------------------
# Main Function
# -------------------------------
def FindAnomaly(ticker: str) -> dict:
    data = dbextract.extract_ticker_data(ticker)
    # Map quarter strings to float values for sorting
    quarter_map = {'Q1': 0.0, 'Q2': 0.25, 'Q3': 0.5, 'Q4': 0.75}
    quarter_data = {}
    for key in data:
        quarter, year = key.split()
        num = float(year) + quarter_map.get(quarter, 0.0)
        quarter_data[num] = data[key]

    # Sort by year+quarter
    sorted_quarters = sorted(quarter_data.items())
    current_year = float(sorted_quarters[-1][0])
    current_metrics = sorted_quarters[-1][1]
    past_years = dict(sorted_quarters[:-1])

    result = {}
    # Simple Average Comparison
    historical_averages = ComputeSimpleAverages(past_years)
    result["simpleAverages"] = CompareSimpleAverages(current_metrics, historical_averages)
    # Linear Regression Comparison
    result["linearRegression"] = CompareLinearRegression(current_year, current_metrics, past_years)

    df = pd.DataFrame(result).T
    return df.to_dict()


# -------------------------------
# Helper Functions
# -------------------------------
def ComputeLRPredictedValue(currentYear, currentYearValue, metricDict):
    threshold = 0.1
    years = np.array(list(metricDict.keys())).reshape(-1, 1)
    values = np.array(list(metricDict.values()))
    model = LinearRegression()
    model.fit(years, values)
    # Require at least some fit quality
    if model.score(years, values) < 0.7:
        return "Model not valid"
    predicted = model.predict(np.array([[currentYear]]))[0]
    diff_ratio = (currentYearValue - predicted) / abs(predicted)
    if diff_ratio > threshold:
        return "Higher than expected"
    elif diff_ratio < -threshold:
        return "Lower than expected"
    return "Changes within the tolerable range"

def CompareLinearRegression(currentYear, currentYearDict, pastYearsDict):
    metric_history = {key: {} for key in currentYearDict}
    for year, metrics in pastYearsDict.items():
        for key, value in metrics.items():
            if key in metric_history:
                metric_history[key][float(year)] = value
    result = {}
    for key, history in metric_history.items():
        if not history:
            result[key] = "No Historical Data"
        else:
            result[key] = ComputeLRPredictedValue(currentYear, currentYearDict[key], history)
    return result

# Compute the historical averages for comparison
def ComputeSimpleAverages(pastYearsDict):
    sums = {}
    counts = {}
    for metrics in pastYearsDict.values():
        for metric, value in metrics.items():
            sums[metric] = sums.get(metric, 0) + value
            counts[metric] = counts.get(metric, 0) + 1
    averages = {metric: sums[metric] / counts[metric] for metric in sums}
    return averages

# Simple Averages Comparison
def CompareSimpleAverages(currentYear, historicalSimpleAverages):
    threshold = 0.1
    changes = {}
    for key, value in currentYear.items():
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
        description="Detects financial anomalies using simple average and regression trend analysis.",
    )