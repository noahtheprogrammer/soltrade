import json
import requests
import pandas as pd
import numpy as np
import talib
from recognition import rankings
from itertools import compress

# This will eventually be filled with miscellaneous algorithms and other such information crucial to trading.
def startTrading():
    print("Merx has now initialized trading.")

# Imports the CryptoCompare API key
def importKey():
        with open('config.json', 'r') as openfile:
            key_object = json.load(openfile)
            x = key_object["api_key"]
            openfile.close
        return x

# Initialize variable to store imported key
api_key = importKey()

# Fetches the CryptoCompare candlestick chart in one hour intervals
def fetchCandlestick():

    # Parameters for use in the json application
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    headers = {'authorization': api_key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Gets candlestick pattern names for analzing
candle_names = talib.get_function_groups()['Pattern Recognition']

# Analyzes the candlestick for most likely pattern
def analyzeCandlestick():

    # Converts fetchCandlestick() response for usage in DataFrame
    candle_json = fetchCandlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time', 'volumefrom', 'volumeto']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # OHLC variables for technical analysis
    op = df['open']
    hi = df['high']
    lo = df['low']
    cl = df['close']

    for candle in candle_names:
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():

        # Runs if no pattern is found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0

        # Runs if a single pattern is found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:

            # A bullish pattern is a 100 or 200 value
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # A bearish pattern is a -100 or -200 value
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1

        # Runs if multiple patterns are found and selects best performing
        else:
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [rankings.candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)

    # Cleans up candlestick dataframe for viewing
    df.drop(candle_names, axis = 1, inplace = True)

analyzeCandlestick()