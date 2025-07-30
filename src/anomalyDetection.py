import pandas as pd
import numpy as np
from src import dbextract
from sklearn.linear_model import LinearRegression

def FindAnomaly(ticker: str) -> pd.DataFrame:
    
    data = dbextract.extract_ticker_data(ticker)

    quarterData = dict()

    for key in data:
        arr = key.split()
        num = float(arr[1])
        if arr[0] == 'Q2':
            num += 0.25
        elif arr[0] == 'Q3':
            num += 0.5
        elif arr[0] == 'Q4':
            num += 0.75
        quarterData[num] = data[key]


    # load and sort the dict (list of tuples)
    totalDict = sorted(quarterData.items())
    
    # current year and past years dict
    currentYear = float(totalDict[-1][0])
    currentYearDict = (totalDict[-1][1])
    pastYearsDict = dict(totalDict[:-1])

    result = dict()
    
    # Comparison 1: Simple Average Comparison
    historicalSimpleAveragesDict = ComputeSimpleAverages(pastYearsDict)
    result["simpleAverages"] = CompareSimpleAverages(currentYearDict, historicalSimpleAveragesDict)
    result["linearRegression"] = CompareLinearRegression(currentYear, currentYearDict, pastYearsDict)

    df = pd.DataFrame(result).T

    return df

def ComputeLRPredictedValue(currentYear, currentYearValue, metricDict):
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

def CompareLinearRegression(currentYear, currentYearDict, pastYearsDict):
    metrics = dict()
    result = dict() # e.g. {'revenueGrowth': positive, 'ebitda': no value}
    for key in currentYearDict:
        metrics[key] = dict()
    
    for year in pastYearsDict:
        particularYear = (pastYearsDict[year])
        for key in particularYear:
            if key in metrics:
                metrics[key][float(year)] = particularYear[key]

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