from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solana.publickey import PublicKey
import base58
import os.path
import json
import requests

# This class holds colors used for error and success messages
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# These are null variables which are assigned depending on the contents within the wallet.json
keypair = None
keypair_seed = None
wallet_address = None

# Checks to determine whether the file exists
def checkJSONState():
    if (os.path.exists("config.json")):

        # Parses the file and assigns the private and public key
        with open('config.json', 'r') as openfile:
            try:
                key_object = json.load(openfile)
                keypair_seed = key_object["private_key"]
                keypair = Keypair.from_secret_key(base58.b58decode(keypair_seed))
                global wallet_address
                wallet_address = keypair.public_key
                openfile.close
                print(colors.OKGREEN + "Merx has successfully imported the private key from the JSON file." + colors.ENDC)
                return True
            except:
                print(colors.WARNING + "Merx was unable to parse the JSON file. Are you sure config.json is formatted properly?" + colors.ENDC)
                return False

    # If unable to find the file, throw out a print() statement
    else:
        print(colors.WARNING + "Merx was unable to detect the JSON file. Are you sure config.json has not been renamed or removed?" + colors.ENDC)
        return False

# Client used for interacting with the Solana network
client = Client("https://api.devnet.solana.com")

# Returns the current balance of Solana in the wallet
def findSolBalance():
    balance_response = client.get_balance(wallet_address).value
    balance_response = balance_response / 1000000000
    return(balance_response)

# Returns the current balance of the USDC token in the wallet
def findUSDCBalance():
    response = client.get_token_accounts_by_owner_json_parsed(wallet_address, TokenAccountOpts(mint = PublicKey("4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"))).to_json()
    json_response = json.loads(response)
    return(json_response["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])

# Returns the current price of Solana using a GET request
def findPrice():
    price_api = 'https://api.coinbase.com/v2/prices/SOL-USD/buy'
    response = requests.get(price_api)
    json_response = response.json()
    return(json_response["data"]["amount"])