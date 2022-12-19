import os
import json
import requests


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

# Fetches the CryptoCompare candlestick chart in 15 minute intervals
def fetchCandlestick():

    # Parameters for use in the json application
    api_key = importKey()
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': api_key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

importKey()
print(fetchCandlestick())