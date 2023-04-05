import requests
import pandas as pd

import backtrader as bt

class merxStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.ind.RSI(self.data.close, period=14)
        self.bb = bt.ind.BollingerBands(self.data.close, period=14)
        self.ema_short = bt.ind.ExponentialMovingAverage(self.data.close, period=5)
        self.ema_medium = bt.ind.ExponentialMovingAverage(self.data.close, period=20)
        self.stoploss = 0
        self.takeprofit = 0

    def next(self):

        if not self.position:
            if self.data.close <= self.stoploss or self.data.close >= self.takeprofit:
                self.close()
            if (self.ema_short > self.ema_medium or self.data.close < self.bb.lines.bot) and self.rsi <= 31:
                self.buy()
                self.stoploss = self.data.close * 0.925
                self.takeprofit = self.data.close * 1.25
        else:
            if (self.ema_short < self.ema_medium or self.data.close > self.bb.lines.top) and self.rsi >= 68:
                self.close()

def format_data():

    url = "https://api.binance.us/api/v3/klines"
    params = {'symbol': 'SOLUSDT', 'interval': '5m', 'limit': 1000}
    response = requests.get(url, params=params)
    candle_dict = response.json()

    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'CT', 'QV', 'N', 'TB', 'TQ', 'I']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], utc=True, unit='ms')
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    formatted_df = df.set_index('time')
    return formatted_df

data = bt.feeds.PandasData(dataname=format_data())

cerebro = bt.Cerebro()
cerebro.addstrategy(merxStrategy)
cerebro.adddata(data)
cerebro.run()
cerebro.plot()