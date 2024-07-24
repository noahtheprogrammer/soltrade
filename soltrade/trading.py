import requests
import asyncio
import pandas as pd

from apscheduler.schedulers.background import BlockingScheduler

from soltrade.transactions import perform_swap, market
from soltrade.indicators import calculate_ema, calculate_rsi, calculate_bbands
from soltrade.strategy import strategy, calc_stoploss, calc_trailing_stoploss
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

    global stoploss, takeprofit, trailing_stoploss, entry_price

    market().load_position()

    # Converts JSON response for DataFrame manipulation
    candle_json = fetch_candlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s') 
    df = strategy(df)
    print(df.tail(2))

    if not MarketPosition().position:
        input_amount = find_balance(config().primary_mint)
        if df['entry'].iloc[-1] == 1:
            buy_msg = f"Soltrade has detected a buy signal using {input_amount} ${config().primary_mint_symbol}."
            log_transaction.info(buy_msg)
            # log_transaction.info(get_statistics())
            if input_amount <= 0:
                fund_msg = f"Soltrade has detected a buy signal, but does not have enough ${config().primary_mint_symbol} to trade."
                log_transaction.info(fund_msg)
                return
            asyncio.run(perform_swap(input_amount, config().primary_mint))
            df['entry_price'] = df['close'].iloc[-1]
            entry_price = df['entry_price']
            df = calc_stoploss(df)
            df = calc_trailing_stoploss(df)
            stoploss = df['stoploss'].iloc[-1]
            trailing_stoploss = df['trailing_stoploss'].iloc[-1]
            print(df.tail(2))
            # Save DataFrame to JSON file
            json_file_path = 'data.json'
            save_dataframe_to_json(df, json_file_path)

            
    else:        
    # Read DataFrame from JSON file
        df = read_dataframe_from_json(json_file_path)
        print(df.tail(2))
        input_amount = find_balance(config().secondary_mint)
        df = calc_trailing_stoploss(df)
        stoploss = df['stoploss'].iloc[-1]
        trailing_stoploss = df['trailing_stoploss'].iloc[-1]
        print(stoploss, trailing_stoploss)
        
        # Check Stoploss
        if df['close'].iloc[-1] <= stoploss:
            sl_msg = f"Soltrade has detected a sell signal for {input_amount} ${config().secondary_mint_symbol}. Stoploss has been reached."
            log_transaction.info(sl_msg)
            # log_transaction.info(get_statistics())
            asyncio.run(perform_swap(input_amount, config().secondary_mint))
            stoploss = takeprofit = 0
            df['entry_price'] = None

        # Check Trailing Stoploss
        if trailing_stoploss is not None:
            if df['close'].iloc[-1] < trailing_stoploss:
                tsl_msg = f"Soltrade has detected a sell signal for {input_amount} ${config().secondary_mint_symbol}. Trailing stoploss has been reached."
                log_transaction.info(tsl_msg)
                # log_transaction.info(get_statistics())
                asyncio.run(perform_swap(input_amount, config().secondary_mint))
                stoploss = takeprofit = 0
                df['entry_price'] = None
            
        # Check Strategy
        if df['exit'].iloc[-1] == 1:
            exit_msg = f"Soltrade has detected a sell signal for {input_amount} ${config().secondary_mint_symbol}."
            log_transaction.info(exit_msg)
            # log_transaction.info(get_statistics())
            asyncio.run(perform_swap(input_amount, config().secondary_mint))
            stoploss = takeprofit = 0
            df['entry_price'] = None

# This starts the trading function on a timer
def start_trading():
    log_general.info("Soltrade has now initialized the trading algorithm.")
    trading_sched = BlockingScheduler()
    trading_sched.add_job(perform_analysis, 'interval', seconds=config().price_update_seconds, max_instances=1)
    trading_sched.start()
    perform_analysis()

# Function to save DataFrame to JSON file
def save_dataframe_to_json(df, file_path):
    df_json = df.to_json(orient='records')
    with open(file_path, 'w') as f:
        json.dump(df_json, f)

# Function to read DataFrame from JSON file
def read_dataframe_from_json(file_path):
    with open(file_path, 'r') as f:
        df_json = json.load(f)
    return pd.read_json(df_json)
