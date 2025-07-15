# Get JSON string with multiple objects. Each object represent a snapshot for the year.

historical = """
{"2019" : { "revenueGrowth": 0.1, "operatingMargin": 0.2 },
"2020" : { "revenueGrowth": 0.2, "operatingMargin": 0.4 },
"2021" : { "revenueGrowth": 0.1, "operatingMargin": 0.1 }}
"""

# Get JSON string with current year's data

current = """
{"revenueGrowth": 0.5, "operatingMargin": 0}
"""

import pandas as pd
import json

def FindAnomaly(historicalJSON, currentJSON):
    historical_dict = json.loads(historicalJSON)
    current_dict = json.loads(currentJSON)
    average_dict = HistoricalMatricesAverages(historical_dict)

    if "revenueGrowth" in current_dict:
        RevenueGrowth(current_dict["revenueGrowth"], average_dict["revenueGrowth"])
    

    return

# Compute the historical averages for comparison
def HistoricalMatricesAverages(historical_dict):
    average_dict = dict()

    for year in historical_dict:
        for metric in historical_dict[year]: 
            if metric in average_dict:
                average_dict[metric] += historical_dict[year][metric]
            else:
                average_dict[metric] = historical_dict[year][metric]
    
    num_year = len(historical_dict)
    for key in average_dict:
        average_dict[key] = average_dict[key] / num_year

    return average_dict


def RevenueGrowth():
    return

def EBITDAMargin():
    return

def OperatingMargin():
    return


def main():
    FindAnomaly(historical, current)




if __name__ == "__main__":
    main()