import backtrader as bt


class SoltradeStrategy(bt.Strategy):
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


class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position
