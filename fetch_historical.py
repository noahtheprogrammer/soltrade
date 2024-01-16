import json, argparse
from datetime import datetime
from time import sleep

import requests
import pandas as pd


parser = argparse.ArgumentParser(description="Script to fetch historical candlestick data for locally running Backtrader strategies")
parser.add_argument("num_records")
parser.add_argument("-t", "--timestamp", required=False, help="A previous toTs to start from")
parser.add_argument("-f", "--file", required=False, help="The path to a previous scrape file to append to")
args = parser.parse_args()

try:
    timestamp = None
    num_records = int(args.num_records)
    if args.timestamp:
        timestamp = int(args.timestamp)
except:
    print(f'Invalid format received: expecting integer')
    exit(1)

if args.file and not args.timestamp:
    print("If a file is provided a timestamp must be provided")
    exit(2)

with open('config.json', 'r') as f:
    config = json.loads(f.read())

def fetch_data(limit=2000, agg=5, toTs=None):
    """
    Fetch data from CryptoCompare of the configured token.
    Inputs can customize the time aggregation and amount of 
    records returned per query.

    Returns a tuple with 0 being the timestamp to begin
    next query to and a dataframe of fetched and formatted data.
    """
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    headers = {'authorization': config['api_key']}
    params = {
        'fsym': config['other_mint_symbol'], 
        'tsym': 'USD', 
        'limit': limit, 
        'aggregate': agg
    }
    if toTs:
        params['toTs'] = toTs
    response = requests.get(url, headers=headers, params=params)
    if response.json()['Response'] == 'Error':
        raise Exception(f'Error while fetching: {response.json()["Message"]}')
    columns = ['time', 'open', 'high', 'low', 'close', 'volumefrom', 'volumeto']
    df = pd.DataFrame(response.json()['Data']['Data'], columns=columns)
    df['time'] = pd.to_datetime(df['time'], utc=True, unit='s')
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volumefrom'])
    formatted_df = df.set_index('time')
    return (response.json()['Data']['TimeFrom'], formatted_df)

if __name__ == '__main__':
    """
    Loop until all records have been found
    or CryptoCompare stops returning results.
    """
    amount_fetched = 0
    toTs = timestamp if args.timestamp else None
    limit = 1500
    agg = 30
    ts = int(datetime.utcnow().timestamp())
    name = f'data/{config["other_mint_symbol"]}-past{num_records}-{ts}.csv'
    if args.file:
        name = args.file
    print(f'[+] Fetching {num_records} records on {agg} minute aggregate for {config["other_mint_symbol"]} to {name}')
    while amount_fetched < num_records:
        print(f'{datetime.utcnow().isoformat()} - fetching next {limit} records {f"until {toTs}" if toTs else ""}')
        if amount_fetched == 0 and not args.timestamp:
            data = fetch_data()
            data[1].to_csv(name)
            toTs = data[0]
        else:
            data = fetch_data(toTs=toTs)
            data[1].to_csv(name, mode='a', header=False)
            toTs = data[0]
        print(f'{datetime.utcnow().isoformat()} - received {len(data[1])} records. Last TimeFrom: {toTs}')
        amount_fetched += limit
        sleep(10)