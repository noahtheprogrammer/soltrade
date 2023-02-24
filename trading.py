import json
import requests
import pandas as pd
import logging
import threading
import talib
import transactions

# Values used to manage trading positions
stoploss, takeprofit = 0
position = False

# This will eventually be filled with miscellaneous algorithms and other such information crucial to trading
def startTrading():
    print("Merx has now initialized trading.")

# Imports the API key
def importKey():
        with open('config.json', 'r') as openfile:
            key_object = json.load(openfile)
            x = key_object["api_key"]
            openfile.close
        return x

# Initialize variable to store imported key
key = importKey()

# Pulls the candlestick information in fifteen minute intervals
def fetchCandlestick():

    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 50, 'aggregate': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Analyzes the current market variables and determines trades
def performAnalysis():
    
    global stoploss
    global takeprofit

    # Converts JSON response for DataFrame manipulation
    candle_json = fetchCandlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time', 'VF', 'VT']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # DataFrame variables for TA-Lib manipulation
    op = df['open']
    hi = df['high']
    lo = df['low']
    cl = df['close']

    # Technical analysis values used in trading algorithm
    ema_short = talib.EMA(cl, timeperiod=5).iat[-1]
    ema_medium = talib.EMA(cl, timeperiod=20).iat[-1]
    rsi = talib.RSI(cl).iat[-1]
    upper_bb, middle_bb, lower_bb = talib.BBANDS(cl, nbdevup=2, nbdevdn=2, timeperiod=14).iat[-1]
    close = cl.iat[-1]
    
    # 
    if not position:
        input_amound = round(current_sol_balance/close, 1) - 0.2
        
        if (ema_short > ema_medium or close < lower_bb) and rsi <= 30:
            transactions.performSwap(input_amount, transactions.usdc_mint)
            stoploss = close * 0.925
            takeprofit = close * 1.25
    else:
        input_amount = round(current_usdc_balance*close, 1) - 0.2
        
        if close <= stoploss or close >= takeprofit:
            transactions.performSwap(input_amount, transactions.sol_mint)
            stoploss, takeprofit = 0
            
        if (ema_short < ema_medium or close > upper_bb) and rsi >= 70:
            transactions.performSwap(input_amount, transactions.sol_mint)
            stoploss, takeprofit = 0

performAnalysis()
