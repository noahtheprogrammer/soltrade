from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solana.publickey import PublicKey
import base58
import os.path
import json
import requests

# These are null variables which are assigned depending on the contents within the wallet.json
keypair = None
keypair_seed = None
wallet_address = None

# Checks to determine whether the file exists
if (os.path.exists("wallet.json")):

    # Parses the file and assigns the private and public key
    with open('wallet.json', 'r') as openfile:
        key_object = json.load(openfile)
        keypair_seed = key_object["private_key"]
        keypair = Keypair.from_secret_key(base58.b58decode(keypair_seed))
        wallet_address = keypair.public_key
        openfile.close

# If unable to find the file, throw out a print() statement
else:
    print("Merx was unable to detect the wallet.json file. Are you sure this file has not been renamed or removed?")

# Client used for interacting with the Solana network
client = Client("https://api.devnet.solana.com")

# Returns the current balance of Solana in the wallet
def findSolBalance():
    balance_response = client.get_balance(wallet_address).value
    balance_response = balance_response / 1000000000
    return(balance_response)

# Returns the current balance of the USDC token in the wallet
def findUSDCBalance():
    usdc_balance = client.get_token_accounts_by_owner_json_parsed(wallet_address, TokenAccountOpts(mint = PublicKey("4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"))).value
    return(usdc_balance)

# Returns the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])
