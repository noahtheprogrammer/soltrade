import requests
import json
import pandas as pd

import backtrader as bt
import yfinance as yf

def importKey():
        with open('config.json', 'r') as openfile:
            key_object = json.load(openfile)
            x = key_object["api_key"]
            openfile.close
        return x

api_key = importKey()

def fetchCandlestick():

    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': api_key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 2000, 'aggregate': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

class merxStrategy(bt.Strategy):
    def __init__(self):
        self.adx = bt.ind.AverageDirectionalMovementIndex(period=12)
        self.ema5, self.ema20, self.ema50 = bt.ind.EMA(period=5), bt.ind.EMA(period=20), bt.ind.EMA(period=50)
        self.rsi = bt.ind.RSI(period=14)
        self.pdi = bt.ind.PlusDirectionalIndicator(period=14)
        self.mdi = bt.ind.MinusDirectionalIndicator(period=14)

    def next(self):
        if self.ema5 < self.ema20 and self.adx >= 25 and self.rsi < 30 or self.pdi > self.mdi:
            self.buy()

        if self.ema5 < self.ema20 < self.ema50 and self.adx >= 25 and self.rsi > 70 or self.mdi > self.pdi:
            self.sell()

def formatData():

    candle_json = fetchCandlestick()
    candle_dict = candle_json["Data"]["Data"]

    columns = ['close', 'high', 'low', 'open', 'time', 'volumefrom', 'volumeto', 'volume']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], utc=True, unit='s')
    df['volume'] = df['volumeto'] + df['volumefrom']
    formatted_df = df.set_index('time')
    return formatted_df

cerebro = bt.Cerebro()
cerebro.addstrategy(merxStrategy)
data = bt.feeds.PandasData(dataname=formatData())
cerebro.adddata(data)
cerebro.run()
cerebro.plot()