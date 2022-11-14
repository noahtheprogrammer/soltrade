from solana.rpc.api import Client
import wallet
import requests

sol_wallet = wallet.keypair
sol_balance = None

# Client used for interacting with the Solana network
client = Client("https://api.devnet.solana.com")

# Returns the current balance of Solana in the wallet
def findSolBalance():
    balance_response = client.get_balance(sol_wallet.public_key)
    return(balance_response)

# Returns the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])