import requests
import asyncio
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler

from soltrade.transactions import perform_swap, market
from soltrade.indicators import calculate_ema, calculate_rsi, calculate_bbands
from soltrade.wallet import find_balance
from soltrade.log import log_general, log_transaction
from soltrade.config import config

market('position.json')

# Stoploss and trading values for statistics and algorithm
stoploss = market().sl
takeprofit = market().tp
ema_short = ema_medium = 0
upper_bb = lower_bb = 0
rsi = 0
price = 0


# Pulls the candlestick information in fifteen minute intervals
def fetch_candlestick():
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': config().api_key}
    params = {'fsym': config().other_mint_symbol, 'tsym': 'USD', 'limit': 50, 'aggregate': config().trading_interval_minutes}
    response = requests.get(url, headers=headers, params=params)
    if response.json().get('Response') == 'Error':
        log_general.error(response.json().get('Message'))
        exit()
    return response.json()

# Analyzes the current market variables and determines trades
def perform_analysis():
    log_general.debug("Soltrade is analyzing the market; no trade has been executed.")

    global stoploss, takeprofit
    global ema_short, ema_medium
    global rsi
    global price
    global upper_bb, lower_bb

    market().load_position()

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

    if not market().position:
        usdc_balance = find_balance(config().usdc_mint)
        input_amount = round(usdc_balance, 1) - 0.01
        if (ema_short > ema_medium or price < lower_bb.iat[-1]) and rsi <= 31:
            log_transaction.info("Soltrade has detected a buy signal.")
            log_transaction.info(get_statistics())
            if input_amount <= 0 or input_amount >= usdc_balance:
                log_transaction.warning("Soltrade has detected a buy signal, but does not have enough USDC to trade.")
                return
            is_swapped = asyncio.run(perform_swap(input_amount, config().usdc_mint))
            if is_swapped:
                stoploss = market().sl = cl.iat[-1] * 0.925
                takeprofit = market().tp = cl.iat[-1] * 1.25
                market().update_position(True, stoploss, takeprofit)
            return
    else:
        input_amount = round(find_balance(config().other_mint), 1) - 0.01

        if price <= stoploss or price >= takeprofit:
            log_transaction.info("Soltrade has detected a sell signal. Stoploss or takeprofit has been reached.")
            log_transaction.info(get_statistics())
            is_swapped = asyncio.run(perform_swap(input_amount, config().other_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

        if (ema_short < ema_medium or price > upper_bb.iat[-1]) and rsi >= 68:
            log_transaction.info("Soltrade has detected a sell signal. EMA or BB has been reached.")
            log_transaction.info(get_statistics())
            is_swapped = asyncio.run(perform_swap(input_amount, config().other_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

# This starts the trading function on a timer
def start_trading():
    log_general.info("Soltrade has now initialized the trading algorithm.")
    log_general.debug("Available commands are statistics, pause, resume, and quit.")

    trading_sched = BackgroundScheduler()
    trading_sched.add_job(perform_analysis, 'interval', seconds=config().price_update_seconds, max_instances=1)
    trading_sched.start()
    perform_analysis()

    while True:
        event = input()
        if event == 'pause':
            trading_sched.pause()
            log_general.info("Soltrade has now been paused.")
        elif event == 'resume':
            trading_sched.resume()
            log_general.info("Soltrade has now been resumed.")
        elif event == 'statistics':
            print_statistics()
        elif event == 'quit':
            log_general.info("Soltrade has now been shut down.")
            exit()
        else:
            log_general.warning("Soltrade does not recognize that command.")

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