from solana.keypair import Keypair
import base58
import os.path
import json

# These are null variables which are assigned depending on the contents within the wallet.json
keypair = None
keypair_seed = None

# Checks to determine whether the file exists
if (os.path.exists("wallet.json")):

    # Parses the file and assigns the private and public key
    with open('wallet.json', 'r') as openfile:
        key_object = json.load(openfile)
        keypair_seed = key_object["private_key"]
        keypair = Keypair.from_secret_key(base58.b58decode(keypair_seed))
        openfile.close

# If unable to find the file, throw out a print() statement
else:
    print("Merx was unable to detect the wallet.json file. Are you sure this file has not been renamed or removed?")