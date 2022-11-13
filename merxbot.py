import requests

# Returns the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])

# Variables that store counts of Solana and USDC tokens
# These are hardcoded for our basic purposes right now but will eventually be read from a wallet
sol_count = 0
usdc_count = 0

sol_value = sol_count * findPrice()
usdc_value = usdc_count