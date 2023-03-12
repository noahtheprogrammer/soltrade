import os.path

import json

import base58
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solana.publickey import PublicKey

# This class holds colors used for error and success messages
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Called in order to natively display colors in Windows
os.system("")

# Client used for interacting with the Solana network
# client = Client("https://api.devnet.solana.com")
client = Client("https://api.mainnet-beta.solana.com/")

# These are null variables which are assigned depending on the contents within the wallet.json
keypair = None
keypair_seed = None
wallet_address = None

# Checks to determine whether the file exists
def check_json_state():
    if (os.path.exists("config.json")):

        # Parses the file and assigns the private and public key
        with open('config.json', 'r') as openfile:
            try:
                key_object = json.load(openfile)
                global keypair_seed
                keypair_seed = key_object["private_key"]
                key_object["api_key"]
                global keypair
                keypair = Keypair.from_secret_key(base58.b58decode(keypair_seed))
                global wallet_address
                wallet_address = keypair.public_key
                openfile.close
                print(colors.OKGREEN + "Merx has successfully imported the private keys from the JSON file." + colors.ENDC)
                return True
            except:
                print(colors.WARNING + "Merx was unable to parse the JSON file. Are you sure config.json is formatted properly?" + colors.ENDC)
                return False

    # If unable to find the file, throw out a print() statement
    else:
        print(colors.WARNING + "Merx was unable to detect the JSON file. Are you sure config.json has not been renamed or removed?" + colors.ENDC)
        return False

# Returns the current balance of Solana in the wallet
def find_sol_balance():
    balance_response = client.get_balance(wallet_address).value
    balance_response = balance_response / (10**9)
    return(balance_response)

# Returns the current balance of the USDC token in the wallet
def find_usdc_balance():
    response = client.get_token_accounts_by_owner_json_parsed(wallet_address, TokenAccountOpts(mint = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))).to_json()
    json_response = json.loads(response)
    return(json_response["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])