import httpx
import json
import asyncio
import os

import base64
from solana.rpc.types import TxOpts
from solana.rpc.core import RPCException
from solders.transaction import VersionedTransaction
from solders.signature import Signature
from solders import message

from soltrade.log import log_general, log_transaction
from soltrade.config import config


class MarketPosition:
    def __init__(self, path):
        self.path = path
        self.is_open = False
        self.sl = 0
        self.tp = 0
        self.load_position()
        self.update_position(self.is_open, self.sl, self.tp)

    def load_position(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                position_data = json.load(file)
                self.is_open = position_data["is_open"]
                self.sl = position_data["sl"]
                self.tp = position_data["tp"]
        else:
            self.update_position(self.is_open, self.sl, self.tp)
            
    def update_position(self, position, stoploss, takeprofit):
        self.sl = stoploss
        self.tp = takeprofit
        self.is_open = position
        position_obj = {
            "is_open": position,
            "sl": stoploss,
            "tp": takeprofit
        }
        with open(self.path, 'w') as file:
            json.dump(position_obj, file)

    @property
    def position(self):
        return self.is_open
    
_market_instance = None

def market(path=None):
    global _market_instance
    if _market_instance is None and path is not None:
        _market_instance = MarketPosition(path)
    return _market_instance


# Returns the route to be manipulated in createTransaction()
async def create_exchange(input_amount: int, input_token_mint: str) -> dict:
    log_transaction.info(f"Soltrade is creating exchange for {input_amount} {input_token_mint}")

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
async def create_transaction(quote: dict) -> dict:
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
def send_transaction(swap_transaction: dict, opts: TxOpts) -> Signature:
    raw_txn = VersionedTransaction.from_bytes(base64.b64decode(swap_transaction))
    signature = config().keypair.sign_message(message.to_bytes_versioned(raw_txn.message))
    signed_txn = VersionedTransaction.populate(raw_txn.message, [signature])

    result = config().client.send_raw_transaction(bytes(signed_txn), opts)
    txid = result.value
    log_transaction.info(f"Soltrade TxID: {txid}")
    return txid

def find_transaction_error(txid: Signature) -> dict:
    json_response = config().client.get_transaction(txid, max_supported_transaction_version=0).to_json()
    parsed_response = json.loads(json_response)["result"]["meta"]["err"]
    return parsed_response

def find_last_valid_block_height() -> dict:
    json_response = config().client.get_latest_blockhash(commitment="confirmed").to_json()
    parsed_response = json.loads(json_response)["result"]["value"]["lastValidBlockHeight"]
    return parsed_response

# Uses the previous functions and parameters to exchange Solana token currencies
async def perform_swap(sent_amount: float, sent_token_mint: str):
    global position
    log_general.info("Soltrade is taking a market position.")

    quote = trans = opts = txid = tx_error = None
    is_tx_successful = False

    for i in range(0, 3):
        if not is_tx_successful:
            try:
                quote = await create_exchange(sent_amount, sent_token_mint)
                trans = await create_transaction(quote)
                opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed", last_valid_block_height=find_last_valid_block_height())
                txid = send_transaction(trans["swapTransaction"], opts)
            except Exception:
                if RPCException:
                    log_general.warning(f"Soltrade failed to complete transaction {i}. Retrying.")
                    continue
                else:
                    raise
            for i in range(0, 3):
                try:
                    await asyncio.sleep(35)
                    tx_error = find_transaction_error(txid)
                    if not tx_error:
                        is_tx_successful = True
                        break
                except TypeError:
                    log_general.warning("Soltrade failed to verify the existence of the transaction. Retrying.")
                    continue
        else:
            break

    if tx_error or not is_tx_successful:
        log_general.error("Soltrade failed to complete the transaction due to slippage issues with Jupiter.")
        return False

    if sent_token_mint == config().usdc_mint:
        decimals = config().decimals
        bought_amount = int(quote['outAmount']) / decimals
        log_transaction.info(f"Sold {sent_amount} USDC for {bought_amount:.6f} {config().other_mint_symbol}")
    else:
        usdc_decimals = 10**6 # TODO: make this a constant variable in utils.py
        bought_amount = int(quote['outAmount']) / usdc_decimals
        log_transaction.info(f"Sold {sent_amount} {config().other_mint_symbol} for {bought_amount:.2f} USDC")
    return True
