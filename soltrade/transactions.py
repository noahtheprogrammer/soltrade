import httpx
import json

import base64
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from solders import message

from soltrade.log import log_general, log_transaction
from soltrade.config import config


class MarketPosition:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketPosition, cls).__new__(cls)
            cls._instance._position = False  # Use a different name for the internal attribute
        return cls._instance

    @property
    def position(self):
        return self._instance._position

    @position.setter
    def position(self, value):
        self._instance._position = value


# Returns the route to be manipulated in createTransaction()
async def create_exchange(input_amount, input_token_mint):
    log_transaction.info(f"Creating exchange for {input_amount} {input_token_mint}")

    # Determines what mint address should be used in the api link
    if input_token_mint == config().usdc_mint:
        output_token_mint = config().other_mint
        token_decimals = 10**6  # USDC decimals
    else:
        output_token_mint = config().usdc_mint
        token_decimals = config().decimals
    
    # Finds the response and converts it into a readable array
    api_link = f"https://quote-api.jup.ag/v6/quote?inputMint={input_token_mint}&outputMint={output_token_mint}&amount={int(input_amount * token_decimals)}&slippageBps={config().slippage}"
    log_transaction.info(f"Soltrade API Link: {api_link}")
    async with httpx.AsyncClient() as client:
        response = await client.get(api_link)
        return response.json()


# Returns the swap_transaction to be manipulated in sendTransaction()
async def create_transaction(quote):
    log_transaction.info(f"""Soltrade is creating transaction for the following quote: 
{quote}""")

    # Parameters used for the Jupiter POST request
    parameters = {
        "quoteResponse": quote,
        "userPublicKey": str(config().public_address),
        "wrapUnwrapSOL": True,
        "computeUnitPriceMicroLamports": 20 * 14000  # fee of roughly $.04  :shrug:
    }

    # Returns the JSON parsed response of Jupiter
    async with httpx.AsyncClient() as client:
        response = await client.post("https://quote-api.jup.ag/v6/swap", json=parameters)
        return response.json()


# Deserializes and sends the transaction from the swap information given
def send_transaction(swap_transaction, opts):
    raw_txn = VersionedTransaction.from_bytes(base64.b64decode(swap_transaction))
    signature = config().keypair.sign_message(message.to_bytes_versioned(raw_txn.message))
    signed_txn = VersionedTransaction.populate(raw_txn.message, [signature])

    result = config().client.send_raw_transaction(bytes(signed_txn), opts)
    txid = result.value
    log_transaction.info(f"Soltrade TxID: {txid}")
    return txid

def validate_transaction(txid):
    json_response = config().client.get_signature_statuses([Signature.from_string(txid)]).to_json()
    parsed_response = json.loads(json_response)
    status = parsed_response["result"]["value"][0]
    return status

# Uses the previous functions and parameters to exchange Solana token currencies
async def perform_swap(sent_amount, sent_token_mint):
    global position
    log_general.info("Soltrade is taking a market position.")
    try:
        quote = await create_exchange(sent_amount, sent_token_mint)
        trans = await create_transaction(quote)
        opts = TxOpts(skip_preflight=True, max_retries=3)
        txid = send_transaction(trans["swapTransaction"], opts)

        if validate_transaction(txid) == None:
            for i in range(0,2): # TODO: make this a customizable retry variable in config.json
                quote = await create_exchange(sent_amount, sent_token_mint)
                trans = await create_transaction(quote)
                opts = TxOpts(skip_preflight=True, max_retries=3)
                txid_attempt = send_transaction(trans["swapTransaction"], opts)

                if validate_transaction(txid_attempt) != None:
                    break
            log_transaction.error("Soltrade was unable to take a market position.")
            return

        if sent_token_mint == config().usdc_mint:
            decimals = config().decimals
            bought_amount = int(quote['outAmount']) / decimals
            log_transaction.info(f"Sold {sent_amount} USDC for {bought_amount:.6f} {config().other_mint_symbol}")
        else:
            usdc_decimals = 10**6 # TODO: make this a constant variable in utils.py
            bought_amount = int(quote['outAmount']) / usdc_decimals
            log_transaction.info(f"Sold {sent_amount} {config().other_mint_symbol} for {bought_amount:.2f} USDC")

        MarketPosition().position = sent_token_mint == config().usdc_mint
    except Exception as e:
        log_transaction.error("Soltrade was unable to take a market position.")
        log_transaction.error(f"SoltradeException: {e}")
