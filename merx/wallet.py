import os.path
import json

import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts

from merx.text import colors, timestamp

# Mainnet client for network interaction
client = Client("https://api.mainnet-beta.solana.com/")

# Returns keypair if successfully parsed and error message if unsuccessfull
def check_json_state():
    if (os.path.exists("config.json")):
        with open('config.json', 'r') as openfile:
            try:
                key_object = json.load(openfile)
                keypair_seed = key_object["private_key"]
                key_object["api_key"]
                keypair = Keypair.from_bytes(base58.b58decode(keypair_seed))
                openfile.close
                return keypair
            except:
                print(colors.FAIL + timestamp.find_time() + "Merx was unable to parse the JSON file. Are you sure config.json is formatted properly?" + colors.ENDC)
                return None
    else:
        print(colors.FAIL + timestamp.find_time() + "Merx was unable to detect the JSON file. Are you sure config.json has not been renamed or removed?" + colors.ENDC)
        return False
    
keypair = check_json_state()
public_address = keypair.pubkey()

# Returns the current balance of $SOL in the wallet
def find_sol_balance():
    balance_response = client.get_balance(public_address).value
    balance_response = balance_response / (10**9)
    return(balance_response)

# Returns the current balance of $USDC in the wallet
def find_usdc_balance():
    response = client.get_token_accounts_by_owner_json_parsed(public_address, TokenAccountOpts(mint = Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"))).to_json()
    json_response = json.loads(response)
    return(json_response["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"])