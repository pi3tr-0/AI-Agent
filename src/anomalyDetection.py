# Get JSON string with multiple objects. Each object represent a snapshot for the year.

historical = """
{"2019" : { "revenueGrowth": 0.1, "operatingMargin": 0.2 },
"2020" : { "revenueGrowth": 0.2, "operatingMargin": 0.4 },
"2021" : { "revenueGrowth": 0.3, "operatingMargin": 0.1 },
"2022" : { "revenueGrowth": 0.4, "operatingMargin": 0.2 },
"2023" : { "revenueGrowth": -0.2, "operatingMargin": 0.21, "ebitda": 0 }}
"""

import pandas as pd
import json

def FindAnomaly(historicalJSON: str):
    # load and sort the dict (list of tuples)
    totalDict = sorted((json.loads(historicalJSON)).items())
    
    # current year and past years dict
    currentYearDict = totalDict[-1][1]
    pastYearsDict = dict(totalDict[:-1])
    
    # Comparison 1: Simple Average Comparison
    historicalSimpleAveragesDict = HistoricalSimpleAverages(pastYearsDict)
    simpleAveragesComparison = CompareSimpleAverages(currentYearDict, historicalSimpleAveragesDict)

    print(simpleAveragesComparison)

    return

# Compute the historical averages for comparison
def HistoricalSimpleAverages(pastYearsDict):
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
            changes[key] = "no historical data"
            continue
        change = (currentYear[key] - historicalSimpleAverages[key])/historicalSimpleAverages[key]
        if change > significantValue:
            changes[key] = "increases"
        elif change < -significantValue:
            changes[key] = "decreases"
        else:
            changes[key] = "no significant change"
    return changes

def main():
    FindAnomaly(historical)




if __name__ == "__main__":
    main()