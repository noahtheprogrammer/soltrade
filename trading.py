import json
import requests
import pandas as pd
import talib
import transactions
import wallet
from apscheduler.schedulers.background import BackgroundScheduler
import keyboard

# Values used to manage trading positions
stoploss = takeprofit = 0
position = False

# Imports the API key
def importKey():
        with open('config.json', 'r') as openfile:
            key_object = json.load(openfile)
            x = key_object["api_key"]
            openfile.close
        return x

# Initialize variable to store imported key
key = importKey()

# Pulls the candlestick information in fifteen minute intervals
def fetchCandlestick():

    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': key}
    params = {'fsym': 'SOL', 'tsym': 'USD', 'limit': 50, 'aggregate': 15}
    response = requests.get(url, headers=headers, params=params)
    return(response.json())

# Analyzes the current market variables and determines trades
def performAnalysis():
    
    global stoploss
    global takeprofit

    # Converts JSON response for DataFrame manipulation
    candle_json = fetchCandlestick()
    candle_dict = candle_json["Data"]["Data"]

    # Creates DataFrame for manipulation
    columns = ['close', 'high', 'low', 'open', 'time', 'VF', 'VT']
    df = pd.DataFrame(candle_dict, columns=columns)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # DataFrame variable for TA-Lib manipulation
    cl = df['close']

    # Technical analysis values used in trading algorithm
    ema_short = talib.EMA(cl, timeperiod=5).iat[-1]
    ema_medium = talib.EMA(cl, timeperiod=20).iat[-1]
    rsi = talib.RSI(cl).iat[-1]
    upper_bb, middle_bb, lower_bb = talib.BBANDS(cl, nbdevup=2, nbdevdn=2, timeperiod=14)

    if not position:
        input_amount = round(wallet.findSolBalance() / cl.iat[-1], 1) - 0.2
        
        if (ema_short > ema_medium or cl.iat[-1] < lower_bb.iat[-1]) and rsi <= 30:
            transactions.performSwap(input_amount, transactions.usdc_mint)
            stoploss = cl.iat[-1] * 0.925
            takeprofit = cl.iat[-1] * 1.25
    else:
        input_amount = round(wallet.findUSDCBalance() * cl.iat[-1], 1) - 0.2
        
        if cl.iat[-1] <= stoploss or cl.iat[-1] >= takeprofit:
            transactions.performSwap(input_amount, transactions.sol_mint)
            stoploss = takeprofit = 0
            
        if (ema_short < ema_medium or cl.iat[-1] > upper_bb.iat[-1]) and rsi >= 70:
            transactions.performSwap(input_amount, transactions.sol_mint)
            stoploss = takeprofit = 0

# This starts the trading function on a timer
def startTrading():
    print("Merx has now initialized the trading algorithm.")

    trading_sched = BackgroundScheduler()
    trading_sched.add_job(performAnalysis, 'interval', minutes=15)
    trading_sched.start()
    performAnalysis()

    while True:
        if keyboard.is_pressed("q"):
            print("Merx has now been shut down.")
            exit()

        if keyboard.is_pressed("p"):
            trading_sched.pause()
            print("Merx has now been paused.")

        if keyboard.is_pressed("r"):
            trading_sched.resume()
            print("Merx has now been resumed.")