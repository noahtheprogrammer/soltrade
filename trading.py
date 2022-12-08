import os
import json
from candlestick import candlestick
import pandas as pd
import asyncio
import requests

# Boolean used to determine which Binance API to use
in_united_states = None

# Checks to determine whether the file exists
def checkCountry():
    if (os.path.exists("config.json")):

        # Parses the file and finds boolean to assign to the global variable
        with open('config.json', 'r') as openfile:
            config = json.load(openfile)
            global in_united_states
            in_united_states = config["in_united_states"]
            openfile.close()

# This will eventually be filled with miscellaneous algorithms and other such information crucial to trading.
def startTrading():
    print("Merx has now initialized trading.")

# Checks for any bullish patterns on the latest candlestick
def isBullishCandle(df):

    # Use the pattern recognition provided in the candlestick folder to check if pattern exists
    hammer = candlestick.hammer(df, target='result')
    if (hammer['result'].iat[-1]):
        return True
    engulfing = candlestick.bullish_engulfing(df, target='result')
    if (engulfing['result'].iat[-1]):
        return True
    ms = candlestick.morning_star(df, target='result')
    if (ms['result'].iat[-1]):
        return True
    ms_doji = candlestick.morning_star_doji(df, target='result')
    if (ms_doji['result'].iat[-1]):
        return True
    harami = candlestick.bullish_harami(df, target='result')
    if (harami['result'].iat[-1]):
        return True
    
    # Return false if no bullish pattern is detected
    return False

# Barebones function that finds where the candlestick pattern occurs (the Inverted Hammer in this example)
def analyzeCandlestick():

    # Determines the proper Binance API to use
    url = None
    if (in_united_states == False):
        url = "https://api.binance.com/api/v3/klines"
    else:
        url = "https://api.binance.us/api/v3/klines"

    # Parameters for use in the json application
    params = {'symbol': 'SOLUSDT', 'interval': '15m', 'limit': 5}
    response = requests.get(url, params=params)

    # Converts the JSON response into a DataFrame for candlestick reading
    candlestick_dict = response.json()
    candlestick_df = pd.DataFrame(candlestick_dict, columns=['T', 'open', 'high', 'low', 'close', 'volume', 'CT', 'QV', 'N', 'TB', 'TQ', 'I'])
    candlestick_df['T'] = pd.to_datetime(candlestick_df['T'], unit='ms')
    print(isBullishCandle(candlestick_df))

analyzeCandlestick()