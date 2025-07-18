import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression

# Get JSON string with multiple objects. Each object represent a snapshot for the year.
JSON = """
{"2019" : { "revenueGrowth": 0.1, "operatingMargin": -0.1 },
"2020" : { "revenueGrowth": 0.2, "operatingMargin": -0.2 },
"2021" : { "revenueGrowth": 0.3, "operatingMargin": -0.3 },
"2022" : { "revenueGrowth": 0.4, "operatingMargin": -0.4 },
"2023" : { "revenueGrowth": 0.45, "operatingMargin": -1, "ebitda": 0 }}
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