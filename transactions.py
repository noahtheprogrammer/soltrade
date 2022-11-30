import wallet
import httpx
import base64
import asyncio
import time
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
from solana.transaction import Transaction

# Returns the route to be manipulated in createTransaction()
async def createExchange(input_amount, input_token_mint):

    output_token_mint = None
    token_decimals = None

    # Determines what mint address should be used in the api link
    if (input_token_mint == "So11111111111111111111111111111111111111112"):
        output_token_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        token_decimals = 10**9
    else:
        output_token_mint = "So11111111111111111111111111111111111111112"
        token_decimals = 10**6
    
    # Finds the response and converts it into a readable array
    api_link = f"https://quote-api.jup.ag/v1/quote?inputMint={input_token_mint}&outputMint={output_token_mint}&amount={input_amount * token_decimals}&slippageBps=50&feeBps=50"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_link)
        return(response.json())

# Returns the swap_transaction to be manipulated in sendTransaction()
async def createTransaction(route):

    # Parameters used for the Jupiter POST request
    parameters = {
        "route": route,
        "userPublicKey": str(wallet.wallet_address),
        "wrapUnwrapSOL": True,
        "feeAccount": "6VEv1cnWVBVrPQt9D8zeGS9RzBp9cdF91uiH6mex5ka2"
    }

    # Returns the JSON parsed response of Jupiter
    async with httpx.AsyncClient() as client:
        response = await client.post("https://quote-api.jup.ag/v1/swap", json=parameters)
        return(response.json())

# Deserializes and sends the transaction from the swap information given
def sendTransaction(swap_transaction, opts):

    # Deserializes the transaction for the client to use
    transaction = Transaction.deserialize(base64.b64decode(swap_transaction))

    # Sends and returns the transaction status
    result = wallet.client.send_transaction(transaction, wallet.keypair, opts=opts)
    txid = result.value
    return(txid)

# Uses the previous functions and parameters to exchange Solana token currencies
async def performSwap(sent_amount, sent_token_mint):

    # Creates exchange and transaction values to be used in sendTransaction() calls
    transaction_route = await createExchange(sent_amount, sent_token_mint)
    quote = transaction_route["data"][0]
    trans = await createTransaction(quote)

    # Variables that store each of the transaction values and revert to None if it doesn't exist
    setup_transaction = trans["setupTransaction"] if "setupTransaction" in trans else None
    swap_transaction = trans["swapTransaction"] if "swapTransaction" in trans else None
    cleanup_transaction = trans["cleanupTransaction"] if "cleanupTransaction" in trans else None
    opts = TxOpts(skip_confirmation=False, skip_preflight=True)

    # This sets up the swap transaction and starts by converting the inputed Solana amount into the wSOL equivalent
    if setup_transaction:
        print("Sending setup transaction...")
        sendTransaction(setup_transaction, opts)
    
    # This swaps the Solana or wSOL token from the setup transaction for the USDC token
    if swap_transaction:
    
    # This swaps the Solana or wSOL token from the setup transaction for the USDC token
    if swap_transaction:
        
        # If an error is thrown because the confirmation failed, retry the transaction one more time
        try:
            print("Sending swap transaction...")
            sendTransaction(swap_transaction, opts)
        except:
            print("Retrying swap transaction...")
            sendTransaction(swap_transaction, opts)
    
    # This sends the final transaction in order to complete the swap
    if cleanup_transaction:
        print("Sending cleanup transaction...")
        sendTransaction(cleanup_transaction, opts)
    print("Swap Complete!")
