import json
import requests
import asyncio

import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler

from merx.wallet import *
from merx.transactions import *
from merx.indicators import *
from merx.text import colors, timestamp

# SL/TP and indicator values for usage
stoploss = takeprofit = 0
ema_short = 0
ema_medium = 0
rsi = 0
upper_bb = 0
lower_bb = 0

# Initial and current portfolio values for viewing $USDC net profit
initial = current = find_usdc_balance()

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
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 50, 'aggregate': 5}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Analyzes the current market variables and determines trades
def perform_analysis():
    
    global stoploss
    global takeprofit
    global ema_short, ema_medium
    global rsi
    global upper_bb, lower_bb
    global current

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
        print(timestamp.find_time() + ": Scouting for optimal open positions.")
        input_amount = round(find_sol_balance() / cl.iat[-1], 1) - 0.2
        current = round(find_usdc_balance(), 2)
        
        if (ema_short > ema_medium or cl.iat[-1] < lower_bb.iat[-1]) and rsi <= 31:
            asyncio.run(perform_swap(input_amount, usdc_mint))
            stoploss = cl.iat[-1] * 0.925
            takeprofit = cl.iat[-1] * 1.25
    else:
        print(timestamp.find_time() + ": Scouting for optimal closing positions.")
        input_amount = round(find_usdc_balance() * cl.iat[-1], 1) - 0.2
        current = round(find_sol_balance() * cl.iat[-1], 2)

        if cl.iat[-1] <= stoploss or cl.iat[-1] >= takeprofit:
            asyncio.run(perform_swap(input_amount, sol_mint))
            stoploss = takeprofit = 0
            return
            
        if (ema_short < ema_medium or cl.iat[-1] > upper_bb.iat[-1]) and rsi >= 68:
            asyncio.run(perform_swap(input_amount, sol_mint))
            stoploss = takeprofit = 0

# This starts the trading function on a timer
def start_trading():
    print(colors.OKGREEN + timestamp.find_time() + ": Merx has now initialized the trading algorithm." + colors.ENDC)
    print(colors.OKBLUE + timestamp.find_time() + ": Available commands are /statistics, /pause, /resume, and /quit." + colors.ENDC)

    trading_sched = BackgroundScheduler()
    trading_sched.add_job(perform_analysis, 'interval', minutes=5)
    trading_sched.start()
    perform_analysis()

    while True:
        event = input().lower()
        if event == '/pause':
            trading_sched.pause()
            print("Merx has now been paused.")

        if event == '/resume':
            trading_sched.resume()
            print("Merx has now been resumed.")

        if event == '/statistics':
            net_profit = round(initial - current, 2)
            if net_profit < 0:
                net_profit = colors.FAIL + "$" + str(net_profit) + " ▼" + colors.ENDC
            else:
                net_profit = colors.OKGREEN + "$" + str(net_profit) + " ▲" + colors.ENDC

            print(f"""
    Net Profit                          {net_profit}
    Total Trades                        {trades}
    Short EMA                           {ema_short}
    Medium EMA                          {ema_medium}
    Relative Strength Index             {rsi}
    Upper Bollinger Band                {upper_bb.iat[-1]}
    Lower Bollinger Band                {lower_bb.iat[-1]}
            """)
            
        if event == '/quit':
            print("Merx has now been shut down.")
            exit()