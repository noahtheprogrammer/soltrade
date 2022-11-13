from solana.keypair import Keypair
import base58
import os.path
import json

keypair = None
keypair_seed = None

if (os.path.exists("wallet.json")):
    with open('wallet.json', 'r') as openfile:
        key_object = json.load(openfile)
        keypair_seed = key_object["private_key"]
        keypair = Keypair.from_secret_key(base58.b58decode(keypair_seed))
        openfile.close
else:
    print("Merx was unable to detect the wallet.json file. Are you sure this file has not been renamed or removed?")

print(keypair.public_key)