import httpx

import base64
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders import message
from soltrade.wallet import *

from soltrade.text import colors, timestamp

# Public mint address values
sol_mint = "So11111111111111111111111111111111111111112"
usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Market position
position = False

# Returns the route to be manipulated in createTransaction()
async def create_exchange(input_amount, input_token_mint):

    output_token_mint = None
    token_decimals = None

    # Determines what mint address should be used in the api link
    if (input_token_mint == sol_mint):
        output_token_mint = usdc_mint
        token_decimals = 10**9
    else:
        output_token_mint = sol_mint
        token_decimals = 10**6
    
    # Finds the response and converts it into a readable array
    api_link = f"https://quote-api.jup.ag/v4/quote?inputMint={input_token_mint}&outputMint={output_token_mint}&amount={int(input_amount * token_decimals)}&slippageBps=50"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_link)
        return(response.json())

# Returns the swap_transaction to be manipulated in sendTransaction()
async def create_transaction(route):

    # Parameters used for the Jupiter POST request
    parameters = {
        "route": route,
        "userPublicKey": str(public_address),
        "wrapUnwrapSOL": True
    }

    # Returns the JSON parsed response of Jupiter
    async with httpx.AsyncClient() as client:
        response = await client.post("https://quote-api.jup.ag/v4/swap", json=parameters)
        return(response.json())

# Deserializes and sends the transaction from the swap information given
def send_transaction(swap_transaction, opts):

    raw_txn = VersionedTransaction.from_bytes(base64.b64decode(swap_transaction))
    signature = keypair.sign_message(message.to_bytes_versioned(raw_txn.message))
    signed_txn = VersionedTransaction.populate(raw_txn.message, [signature])

    result = client.send_raw_transaction(bytes(signed_txn), opts)
    txid = result.value

    print(colors.HEADER + timestamp.find_time() + f": Soltrade TxID: {txid}" + colors.ENDC)
    return(txid)

# Uses the previous functions and parameters to exchange Solana token currencies
async def perform_swap(sent_amount, sent_token_mint):

    global position

    try:
        # Creates token exchange and quote
        txn_route = await create_exchange(sent_amount, sent_token_mint)
        quote = txn_route["data"][0]
        trans = await create_transaction(quote)

        opts = TxOpts(skip_preflight=True, max_retries=3)
        send_transaction(trans["swapTransaction"], opts)
                
        if sent_token_mint == usdc_mint:
            print(colors.OKGREEN + timestamp.find_time() + ": Soltrade has successfully opened a market position." + colors.ENDC)
            position = True
        else:
            print(colors.OKGREEN + timestamp.find_time() + ": Soltrade has successfully closed a market position." + colors.ENDC)
            position = False
    except Exception as e:
        print(colors.FAIL + timestamp.find_time() + ": Soltrade was unable to take a market position." + colors.ENDC)
        print(colors.FAIL + timestamp.find_time() + f": SoltradeException: {e}" + colors.ENDC)