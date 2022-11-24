import wallet
import requests

# This will eventually be filled with miscellaneous algorithms and other such information crucial to trading.
def startTrading():
    print("Merx has now initialized trading.")

# This is the barebones structure for creating an exchange with SimpleSwap
# I have reached out about adding a SOL-USDC pair, but will use another noncustodial exchange if not available
def createExchange(sending_ticker, sending_amount):
    api_link = "https://api.simpleswap.io/create_exchange?api_key=365d4d16-7ac8-4c2f-bed3-5f66cbcf0575"
    receiving_ticker = None

    if (sending_ticker == "sol"):
        receiving_ticker = "usdcspl"
    else:
        receiving_ticker = "sol"
    
    exchange_json = {
        "currency_from": sending_ticker,
        "currency_to": receiving_ticker,
        "fixed": False,
        "amount": sending_amount,
        "address_to": wallet.wallet_address,
        "extraIdTo": "",
        "userRefundAddress": wallet.wallet_address,
        "userRefundExtraId": ""
    }

    exchange = requests.post(api_link, exchange_json)
    return(exchange)