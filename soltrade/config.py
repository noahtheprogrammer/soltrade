import os
import json
import base58

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solana.rpc.api import Client
from soltrade.log import log_general
from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()

        self.api_key = None
        self.private_key = None
        self.custom_rpc_https = None
        self.primary_mint = None
        self.primary_mint_symbol = None
        self.sol_mint = "So11111111111111111111111111111111111111112"
        self.secondary_mint = None
        self.secondary_mint_symbol = None
        self.price_update_seconds = None
        self.trading_interval_minutes = None
        self.slippage = None  # BPS
        self.computeUnitPriceMicroLamports = None
        self.load_config()

    def load_config(self):
        self.api_key = os.getenv('API_KEY')
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")
        self.custom_rpc_https = os.getenv("custom_rpc_https", "https://api.mainnet-beta.solana.com/")
        self.primary_mint = os.getenv("PRIMARY_MINT", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        self.primary_mint_symbol = os.getenv("PRIMARY_MINT_SYMBOL", "USD")
        self.secondary_mint = os.getenv("SECONDARY_MINT", "")
        self.secondary_mint_symbol = os.getenv("SECONDARY_MINT_SYMBOL", "UNKNOWN")
        self.price_update_seconds = int(os.getenv("PRICE_UPDATE_SECONDS") or 60)
        self.trading_interval_minutes = int(os.getenv("TRADING_INTERVALS_MINUTE") or 1)
        self.slippage = int(os.getenv("SLIPPAGE") or 50)

        # DEFAULT FEE OF ROUGHLY $0.04 TODAY
        self.computeUnitPriceMicroLamports = int(os.getenv("COMPUTE_UNIT_PRICE_MICRO_LAMPORTS") or 20 * 14000)

    @property
    def keypair(self) -> Keypair:
        try:
            return Keypair.from_bytes(base58.b58decode(self.private_key))
        except Exception as e:
            log_general.error(f"Error decoding private key: {e}")
            exit(1)

    @property
    def public_address(self) -> Pubkey:
        return self.keypair.pubkey()

    @property
    def client(self) -> Client:
        rpc_url = self.custom_rpc_https
        return Client(rpc_url)

    @property
    def decimals(self) -> int:
        response = self.client.get_account_info_json_parsed(Pubkey.from_string(config().secondary_mint)).to_json()
        json_response = json.loads(response)
        value = 10 ** json_response["result"]["value"]["data"]["parsed"]["info"]["decimals"]
        return value


_config_instance = None


def config() -> Config:
    global _config_instance
    _config_instance = Config()
    return _config_instance
