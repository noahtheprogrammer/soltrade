import os
import json
import asyncio
import requests

# Boolean used to determine which Binance API to use
in_united_states = None

# Checks to determine whether the file exists
def checkIfUnitedStates():
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

# Fetches the Binance candlestick chart in 15 minute intervals
def fetchCandlestick():

    # Determines the proper Binance API to use
    url = None
    if (in_united_states == False):
        url = "https://api.binance.com/api/v3/klines"
    else:
        url = "https://api.binance.us/api/v3/klines"

    # Parameters for use in the json application
    params = {'symbol': 'SOLUSDT', 'interval': '15m'}
    response = requests.get(url, params=params)
    return(response.json())