
import json

from solders.pubkey import Pubkey
from solana.rpc.types import TokenAccountOpts

from soltrade.utils import handle_rate_limiting
from soltrade.config import config


# Returns the current balance of token in the wallet
@handle_rate_limiting()
def find_balance(token_mint):

    response = config().client.get_token_accounts_by_owner_json_parsed(config().public_address, TokenAccountOpts(
        mint=Pubkey.from_string(token_mint))).to_json()
    json_response = json.loads(response)
    if len(json_response["result"]["value"]) == 0:
        return 0
    return json_response["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
