import json
import requests
import pandas as pd
import numpy as np
import logging
import threading
import talib
import transactions
from recognition import fear
from recognition import rankings
from itertools import compress

import test_values

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

last_traded_sol_price = None
last_traded_coin = "sol"

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

# Fetches the OHLCV information in fifteen minute intervals
def fetchCandlestick():

    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': api_key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 50, 'aggregate': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Basic trading algorithm that determines what trade to perform with parameters
def determineTrade(pattern, ema5, ema20, adx, obv, fgi, current_sol_price):

    current_sol_balance = test_values.sol_balance
    current_usdc_balance = test_values.usdc_balance

    global last_traded_coin
    global last_traded_sol_price

    if ("_Bull" in pattern):
        if ((obv > 0) or (adx >= 25) or (ema5 - ema20 > 0)):
            if (last_traded_coin == "usdc"):
                logging.info(f"BULLISH_TRADE_{current_usdc_balance}USDC_TO_{(current_usdc_balance)/current_sol_price}SOL_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}")
                test_values.performSwap(current_usdc_balance, transactions.usdc_mint, current_sol_price)
                last_traded_sol_price = current_sol_price
                last_traded_coin = "sol"
            else:
                logging.info(f"BULLISH_HOLD_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}_SOLBALANCE{current_sol_balance}_USDCBALANCE{current_usdc_balance}")

        else:
            if ((last_traded_coin == "usdc")):
                logging.info(f"BULLISH_BREAKOUT_TRADE_{current_usdc_balance}USDC_TO_{(current_usdc_balance)/current_sol_price}SOL_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}")
                test_values.performSwap(current_usdc_balance, transactions.usdc_mint, current_sol_price)
                last_traded_sol_price = current_sol_price
                last_traded_coin = "sol"
            else:
                logging.info(f"BULLISH_BREAKOUT_HOLD_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}_SOLBALANCE{current_sol_balance}_USDCBALANCE{current_usdc_balance}")

    if ("_Bear" in pattern):

        if ((obv < 0) or (adx >= 25) or (ema5 - ema20 < 0)):
            if (last_traded_coin == "sol"):
                logging.info(f"BEARISH_TRADE_{current_sol_balance}SOL_TO_{current_sol_balance * current_sol_price}USDC")
                test_values.performSwap(current_sol_balance, transactions.sol_mint, current_sol_price)
                last_traded_sol_price = current_sol_price
                last_traded_coin = "usdc"
            else:
                logging.info(f"BEARISH_HOLD_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}_SOLBALANCE{current_sol_balance}_USDCBALANCE{current_usdc_balance}")

        else:
            if ((last_traded_coin == "sol")):
                logging.info(f"BEARISH_BREAKOUT_TRADE_{current_sol_balance}SOL_TO_{current_sol_balance * current_sol_price}USDC")
                test_values.performSwap(current_sol_balance, transactions.sol_mint, current_sol_price)
                last_traded_sol_price = current_sol_price
                last_traded_coin = "usdc"
            else:
                logging.info(f"BEARISH_BREAKOUT_HOLD_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}_SOLBALANCE{current_sol_balance}_USDCBALANCE{current_usdc_balance}")

    if ("NO_PATTERN" in pattern):
        logging.info(f"NO_TRADE_PERFORMED_ADX{adx}_OBV{obv}_FGI{fgi}_PRICE{current_sol_price}_SOLBALANCE{current_sol_balance}_USDCBALANCE{current_usdc_balance}")


# Analyzes the candlestick for most likely pattern
def performAnalysis():

    threading.Timer(900.0, performAnalysis).start()

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
    vl = df['volumeto'] + df['volumefrom']

    # DataFrames for technical analysis
    adx_df = talib.ADX(hi, lo, cl, timeperiod=12)
    ema5_df = talib.EMA(cl, timeperiod=5)
    ema20_df = talib.EMA(cl, timeperiod=20)
    obv_df = talib.OBV(cl, vl)

    # Returns the daily crypto FGI
    fgi = fear.findFGI()
    
    # Gets candlestick pattern names for analzing
    candle_names = talib.get_function_groups()['Pattern Recognition']

    for candle in candle_names:
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    # Patterns we have decided to exclude
    excluded_names = ('CDLCOUNTERATTACK',
                     'CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN',
                     'CDLKICKINGBYLENGTH')

    # Uses above variable to exclude specific patterns
    candle_names = [candle for candle in candle_names if candle not in excluded_names]

    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
    for index, row in df.iterrows():

        # Runs if no pattern is found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0

        # Runs if a single pattern is found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:

            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1

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
    df.drop(candle_names + list(excluded_names), axis = 1, inplace = True)
    determineTrade(df['candlestick_pattern'].iat[-1], ema5_df.iat[-1], ema20_df.iat[-1], adx_df.iat[-1], obv_df.iat[-1], fgi, cl.iat[-1])

performAnalysis()