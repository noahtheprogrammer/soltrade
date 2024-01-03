import requests
import asyncio
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler

from soltrade.transactions import perform_swap, position
from soltrade.indicators import calculate_ema, calculate_rsi, calculate_bbands
from soltrade.utils import timestamp
from soltrade.wallet import find_balance
from soltrade.log import log_general, log_transaction
from soltrade.config import config


# Stoploss and trading values for statistics and algorithm
stoploss = takeprofit = 0
ema_short = ema_medium = 0
upper_bb = lower_bb = 0
rsi = 0
price = 0


# Pulls the candlestick information in fifteen minute intervals
def fetch_candlestick():
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': config().api_key}
    params = {'fsym': config().other_mint_symbol, 'tsym': 'USD', 'limit': 50, 'aggregate': 5}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# Analyzes the current market variables and determines trades
def perform_analysis():
    log_general.debug(timestamp() + ": Soltrade is analyzing the market.")

    global stoploss
    global takeprofit
    global ema_short, ema_medium
    global rsi
    global price
    global upper_bb, lower_bb

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
    price = cl.iat[-1]
    ema_short = calculate_ema(dataframe=df, length=5)
    ema_medium = calculate_ema(dataframe=df, length=20)
    rsi = calculate_rsi(dataframe=df, length=14)
    upper_bb, lower_bb = calculate_bbands(dataframe=df, length=14)

    log_general.debug(get_statistics())

    if not position:
        input_amount = round(find_balance(config().usdc_mint), 1) - 2  # TODO: make this configurable
        if (ema_short > ema_medium or price < lower_bb.iat[-1]) and rsi <= 31:
            log_transaction.info(timestamp() + ": Soltrade has detected a buy signal.")
            log_transaction.info(get_statistics())
            asyncio.run(perform_swap(input_amount, config().usdc_mint))
            stoploss = cl.iat[-1] * 0.925
            takeprofit = cl.iat[-1] * 1.25
    else:
        input_amount = round(find_balance(config().other_mint), 1) - 0.2

        if price <= stoploss or price >= takeprofit:
            message = timestamp() + ": Soltrade has detected a sell signal. Stoploss or takeprofit has been reached."
            log_transaction.info(message)
            log_transaction.info(get_statistics())
            asyncio.run(perform_swap(input_amount, config().other_mint_symbol))
            stoploss = takeprofit = 0
            return

        if (ema_short < ema_medium or price > upper_bb.iat[-1]) and rsi >= 68:
            message = timestamp() + ": Soltrade has detected a sell signal. EMA or BB has been reached."
            log_transaction.info(message)
            log_transaction.info(get_statistics())
            asyncio.run(perform_swap(input_amount, config().other_mint_symbol))
            stoploss = takeprofit = 0


# This starts the trading function on a timer
def start_trading():
    log_general.info(timestamp() + ": Soltrade has now initialized the trading algorithm.")
    log_general.debug(": Available commands are /statistics, /pause, /resume, and /quit.")

    trading_sched = BackgroundScheduler()
    trading_sched.add_job(perform_analysis, 'interval', seconds=config().trading_interval_seconds, max_instances=1)
    trading_sched.start()
    perform_analysis()

    while True:
        event = input().lower()
        if event == '/pause':
            trading_sched.pause()
            log_general.info("Soltrade has now been paused.")

        if event == '/resume':
            trading_sched.resume()
            log_general.info("Soltrade has now been resumed.")
        if event == '/statistics':
            print_statistics()

        if event == '/quit':
            log_general.info("Soltrade has now been shut down.")
            exit()


def get_statistics():
    return f"""
        Short EMA                           {ema_short}
        Medium EMA                          {ema_medium}
        Relative Strength Index             {rsi}
        Price                               {price}
        Upper Bollinger Band                {upper_bb.iat[-1]}
        Lower Bollinger Band                {lower_bb.iat[-1]}"""


def print_statistics():
    log_general.debug(get_statistics())
