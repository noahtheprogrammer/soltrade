import requests
import asyncio
import pandas as pd

from apscheduler.schedulers.background import BlockingScheduler

from soltrade.transactions import perform_swap, market
from soltrade.indicators import calculate_ema, calculate_rsi, calculate_bbands
from soltrade.wallet import find_balance
from soltrade.log import log_general, log_transaction
from soltrade.config import config

market('position.json')

# Pulls the candlestick information in fifteen minute intervals
def fetch_candlestick() -> dict:
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': config().api_key}
    params = {'tsym': config().primary_mint_symbol, 'fsym': config().secondary_mint_symbol, 'limit': 50, 'aggregate': config().trading_interval_minutes}
    response = requests.get(url, headers=headers, params=params)
    if response.json().get('Response') == 'Error':
        log_general.error(response.json().get('Message'))
        exit()
    return response.json()

# Analyzes the current market variables and determines trades
def perform_analysis():
    log_general.debug("Soltrade is analyzing the market; no trade has been executed.")

    global stoploss, takeprofit

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
    stoploss = market().sl
    takeprofit = market().tp

    log_general.debug(f"""
price:                  {price}
short_ema:              {ema_short}
med_ema:                {ema_medium}
upper_bb:               {upper_bb.iat[-1]}
lower_bb:               {lower_bb.iat[-1]}
rsi:                    {rsi}
stop_loss               {stoploss}
take_profit:            {takeprofit}
""")

    if not market().position:
        input_amount = find_balance(config().primary_mint)

        if (ema_short > ema_medium or price < lower_bb.iat[-1]) and rsi <= 31:
            log_transaction.info("Soltrade has detected a buy signal.")
            if input_amount <= 0:
                log_transaction.warning(f"Soltrade has detected a buy signal, but does not have enough {config().primary_mint_symbol} to trade.")
                return
            is_swapped = asyncio.run(perform_swap(input_amount, config().primary_mint))
            if is_swapped:
                stoploss = market().sl = cl.iat[-1] * 0.925
                takeprofit = market().tp = cl.iat[-1] * 1.25
                market().update_position(True, stoploss, takeprofit)
            return
    else:
        input_amount = find_balance(config().secondary_mint)
        
        # sometimes position.json might contain wrong or outdated data
        if input_amount == 0.0:
            stoploss = takeprofit = market().sl = market().tp = 0
            market().update_position(False, stoploss, takeprofit)
            log_transaction.info("Soltrade has detected outdated data in position.json. Reseting position.")
            return

        if price <= stoploss or price >= takeprofit:
            log_transaction.info("Soltrade has detected a sell signal. Stoploss or takeprofit has been reached.")
            is_swapped = asyncio.run(perform_swap(input_amount, config().secondary_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

        if (ema_short < ema_medium or price > upper_bb.iat[-1]) and rsi >= 68:
            log_transaction.info("Soltrade has detected a sell signal. EMA or BB has been reached.")
            is_swapped = asyncio.run(perform_swap(input_amount, config().secondary_mint))
            if is_swapped:
                stoploss = takeprofit = market().sl = market().tp = 0
                market().update_position(False, stoploss, takeprofit)
            return

# This starts the trading function on a timer
def start_trading():
    log_general.info("Soltrade has now initialized the trading algorithm.")

    trading_sched = BlockingScheduler()
    trading_sched.add_job(perform_analysis, 'interval', seconds=config().price_update_seconds, max_instances=1)
    trading_sched.start()
    perform_analysis()