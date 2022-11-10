import requests

# Function used to return the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])

wallet_coins = 0
initial_value = wallet_coins * findPrice()
inital_price = findPrice()