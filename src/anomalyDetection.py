import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression

# Get JSON string with multiple objects. Each object represent a snapshot for the year.
JSON = """
{ "2021": { "totalRevenue": 365817000000.0, "ebitda": 123136000000.0, "ebitdaMargin": 0.33660546120054563, "operatingMargin": 0.29782377527561593, "netIncome": 94680000000.0, "profitMargin": 0.2588179335569424 }, "2022": { "totalRevenue": 394328000000.0, "revenueGrowth": 0.0779378760418461, "ebitda": 130541000000.0, "ebitdaMargin": 0.3310467428130896, "operatingMargin": 0.30288744395528594, "netIncome": 99803000000.0, "profitMargin": 0.2530964070519973 }, "2023": { "totalRevenue": 383285000000.0, "revenueGrowth": -0.02800460530319937, "ebitda": 125820000000.0, "ebitdaMargin": 0.3282674772036474, "operatingMargin": 0.2982141226502472, "netIncome": 96995000000.0, "profitMargin": 0.2530623426432028 }, "2024": { "totalRevenue": 391035000000.0, "revenueGrowth": 0.02021994077514111, "ebitda": 134661000000.0, "ebitdaMargin": 0.3443707085043538, "operatingMargin": 0.31510222870075566, "netIncome": 93736000000.0, "profitMargin": 0.23971255769943867 }, "2025": { "sharesOutstanding": 14935799808.0, "trailingEps": 6.42, "dividendsPerShare": 1.04, "dividendYield": 0.51, "priceSalesRatio": 7.926644, "priceEarningsRatio": 33.096573, "priceBookRatio": 47.52404, "evEbitda": 22.42501039441189, "roa": 0.23809999, "roe": 1.38015 } }
"""

def FindAnomaly(JSON: str):

    result = dict()
    
    # load and sort the dict (list of tuples)
    totalDict = sorted((json.loads(JSON)).items())
    
    # current year and past years dict
    currentYear = int(totalDict[-1][0])
    currentYearDict = totalDict[-1][1]
    pastYearsDict = dict(totalDict[:-1])
    
    # Comparison 1: Simple Average Comparison
    historicalSimpleAveragesDict = ComputeSimpleAverages(pastYearsDict)
    result["simpleAverages"] = CompareSimpleAverages(currentYearDict, historicalSimpleAveragesDict)
    result["linearRegression"] = CompareLinearRegression(currentYear, currentYearDict, pastYearsDict)

    df = pd.DataFrame(result).T

    return df

def ComputeLRPredictedValue(currentYear: int, currentYearValue, metricDict):
    significantValue = 0.1

    x = np.array(list(metricDict.keys())).reshape(-1, 1)
    y = np.array(list(metricDict.values()))

    model = LinearRegression()
    model.fit(x, y)

    if model.score(x, y) < 1:
        return "model not valid"
    
    new_x = np.array([[currentYear]])
    predicted_y = model.predict(new_x)

    difference = (currentYearValue - predicted_y) / abs(predicted_y)

    if (difference > significantValue):
        return "Higher than expected"
    elif (difference < -significantValue):
        return "Lower than expected"
    else:
        return "Changes within the tolerable range"

def CompareLinearRegression(currentYear: int, currentYearDict, pastYearsDict):
    metrics = dict()
    result = dict() # e.g. {'revenueGrowth': positive, 'ebitda': no value}
    for key in currentYearDict:
        metrics[key] = dict()
    
    for year in pastYearsDict:
        particularYear = (pastYearsDict[year])
        for key in particularYear:
            if key in metrics:
                metrics[key][int(year)] = particularYear[key]

    for key in metrics:
        if len(metrics[key]) == 0:
            result[key] = "No Historical Data"
        else:
            result[key] = ComputeLRPredictedValue(currentYear,currentYearDict[key],metrics[key])
    
    return result

# Compute the historical averages for comparison
def ComputeSimpleAverages(pastYearsDict):
    averageDict = dict()

    for year in pastYearsDict:
        for metric in pastYearsDict[year]: 
            if metric in averageDict:
                averageDict[metric] += pastYearsDict[year][metric]
            else:
                averageDict[metric] = pastYearsDict[year][metric]

    num_year = len(pastYearsDict)
    for key in averageDict:
        averageDict[key] = averageDict[key] / num_year

    return averageDict

# Simple Averages Comparison
def CompareSimpleAverages(currentYear, historicalSimpleAverages):
    significantValue = 0.1 # % change threshold

    changes = dict() # record changes (if any) in a dict

    for key in currentYear:
        if key not in historicalSimpleAverages: # edgecase: no historical data
            changes[key] = "No historical data"
            continue
        change = (currentYear[key] - historicalSimpleAverages[key])/abs(historicalSimpleAverages[key])
        if change > significantValue:
            changes[key] = "Higher than expected"
        elif change < -significantValue:
            changes[key] = "Lower than expected"
        else:
            changes[key] = "Changes within the tolerable range"
    return changes