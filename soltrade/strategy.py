import pandas as pd
import pandas_ta as pta
import talib.abstract as ta
from soltrade.config import config
from soltrade.log import log_general

def strategy(df: pd.DataFrame):
    if config().strategy == 'default' or None:
        if config().strategy is None:
            log_general.info("No strategy selected in config.json using default")

        ### Populate default indicators
        # Calculates EMA 
        df['ema_s'] = ta.EMA(df['close'], timeperiod = 8)
        df['ema_m'] = ta.EMA(df['close'], timeperiod = 21)

        # Bollinger Bands
        sma = ta.SMA(df['close'], timeperiod = 20)
        std = df['close'].rolling(20).std()
        df['upper_bband'] = sma + std * 2
        df['lower_bband'] = sma - std * 2

        # RSI        
        df['rsi'] = ta.RSI(df, timeperiod=14)
        

        ### Entry
        entry = (
            ((df['ema_s'] > df['ema_m']) |
            (df['close'] < df['lower_bband'])) &
            (df['rsi'] <= 31)
        )
        df.loc[entry, 'entry'] = 1


        ### Exit
        exit = (
            ((df['ema_s'] < df['ema_m']) |
            (df['close'] > df['upper_bband'])) &
            (df['rsi'] >= 65)
        )
        df.loc[exit, 'exit'] = 1

    return df
    
    if config().strategy == 'custom':

        df['cci'] = ta.CCI(df)


    
def calc_stoploss(df):
    # Can also write custom stoploss functions using indicators.
    sl = float(config().stoploss)

    df['stoploss'] = df['entry_price'].iloc[-1] * (1 - sl / 100)
    
    return df

def calc_trailing_stoploss(df):
    # Can also write custom stoploss functions using indicators.
    tsl = float(config().trailing_stoploss)
    tslt = float(config().trailing_stoploss_target)

    high_prices = df['high']
    df['entry_price'] * (1 + tslt / 100)
    trailing_stop = []
    tracking_started = False  # Flag to indicate when to start tracking the trailing stop-loss
    highest_price = df['high'].iloc[0]

    for price in high_prices:
        if not tracking_started and price >= df['entry_price'].iloc[0] * (1 + tslt / 100):
            # Start tracking the trailing stop-loss once the target price is reached
            tracking_started = True
            stop_price = highest_price * (1 - tsl / 100)
        elif tracking_started:
            if price > highest_price:
                highest_price = price
            stop_price = highest_price * (1 - tsl / 100)

        trailing_stop.append(stop_price if tracking_started else None)

    df['trailing_stoploss'] = trailing_stop
    df['trailing_stoploss_target'] = df['entry_price'] * (1 + tslt / 100)

    return df



