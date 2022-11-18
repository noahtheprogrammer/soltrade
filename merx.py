from solana.rpc.api import Client
import wallet
import requests

sol_wallet = wallet.keypair.public_key

# Client used for interacting with the Solana network
client = Client("https://api.devnet.solana.com")

# Returns the current balance of Solana in the wallet
def findSolBalance():
    balance_response = client.get_balance(sol_wallet).value
    balance_response = balance_response / 1000000000
    return(balance_response)

# Returns the current balance of USDC in the wallet
# Currently not functional but I will find the proper method to use
def findUSDCBalance():
    usdc_balance = client.get_token_account_balance(sol_wallet).value.amount
    return(usdc_balance)

sol_balance = findSolBalance()

# Returns the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])