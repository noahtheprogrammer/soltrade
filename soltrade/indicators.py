import pandas as pd


# Calculates EMA using DataFrame
def calculate_ema(dataframe: pd.DataFrame, length: int) -> int:
    ema = dataframe['close'].ewm(span=length, adjust=False).mean()
    return ema.iat[-1]


# Calculates BB using SMA indicator and DataFrame
def calculate_bbands(dataframe: pd.DataFrame, length: int) -> pd.Series:
    sma = dataframe['close'].rolling(length).mean()
    std = dataframe['close'].rolling(length).std()
    upper_bband = sma + std * 2
    lower_bband = sma - std * 2
    return upper_bband, lower_bband


# Calculates RSI using custom EMA indicator and DataFrame
def calculate_rsi(dataframe: pd.DataFrame, length: int) -> int:
    delta = dataframe['close'].diff()
    up = delta.clip(lower=0)
    down = delta.clip(upper=0).abs()
    upper_ema = up.ewm(com=length - 1, adjust=False, min_periods=length).mean()
    lower_ema = down.ewm(com=length - 1, adjust=False, min_periods=length).mean()
    rsi = upper_ema / lower_ema
    rsi = 100 - (100 / (1 + rsi))
    return rsi.iat[-1]
