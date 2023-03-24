import json
import requests
import asyncio

import pandas as pd

import keyboard
from apscheduler.schedulers.background import BackgroundScheduler

from merx.wallet import *
from merx.transactions import *
from merx.indicators import *
from merx.text import colors, timestamp

# Values used to manage trading positions
stoploss = takeprofit = 0
position = False

# Imports the API key
def import_key():
        with open('config.json', 'r') as openfile:
            key_object = json.load(openfile)
            x = key_object["api_key"]
            openfile.close
        return x

# Initialize variable to store imported key
key = import_key()

# Pulls the candlestick information in fifteen minute intervals
def fetch_candlestick():

    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 50, 'aggregate': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Analyzes the current market variables and determines trades
def perform_analysis():
    
    global stoploss
    global takeprofit

    # Converts JSON response for DataFrame manipulation
    candle_json = fetch_candlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time', 'VF', 'VT']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # DataFrame variable for TA-Lib manipulation
    cl = df['close']

    # Technical analysis values used in trading algorithm
    ema_short = calculate_ema(dataframe=df, length=5)
    ema_medium = calculate_ema(dataframe=df, length=20)
    rsi = calculate_rsi(dataframe=df, length=14)
    upper_bb, lower_bb = calculate_bbands(dataframe=df, length=14)

    if not position:
        input_amount = round(find_sol_balance() / cl.iat[-1], 1) - 0.2
        
        if (ema_short > ema_medium or cl.iat[-1] < lower_bb.iat[-1]) and rsi <= 30:
            asyncio.run(perform_swap(input_amount, usdc_mint))
            stoploss = cl.iat[-1] * 0.925
            takeprofit = cl.iat[-1] * 1.25
    else:
        input_amount = round(find_usdc_balance() * cl.iat[-1], 1) - 0.2
        
        if cl.iat[-1] <= stoploss or cl.iat[-1] >= takeprofit:
            asyncio.run(perform_swap(input_amount, sol_mint))
            stoploss = takeprofit = 0
            
        if (ema_short < ema_medium or cl.iat[-1] > upper_bb.iat[-1]) and rsi >= 70:
            asyncio.run(perform_swap(input_amount, sol_mint))
            stoploss = takeprofit = 0

# This starts the trading function on a timer
def start_trading():
    print(colors.OKGREEN + timestamp.TIME + ": Merx has now initialized the trading algorithm." + colors.ENDC)

    trading_sched = BackgroundScheduler()
    trading_sched.add_job(perform_analysis, 'interval', minutes=15)
    trading_sched.start()
    perform_analysis()

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'p':
                keyboard.wait('p')
                trading_sched.pause()
                print("Merx has now been paused.")

            if event.name == 'r':
                keyboard.wait('r')
                trading_sched.resume()
                print("Merx has now been resumed.")
            
            if event.name == 'q':
                keyboard.wait('q')
                print("Merx has now been shut down.")
                exit()