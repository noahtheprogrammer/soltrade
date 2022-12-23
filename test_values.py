sol_balance = 100
usdc_balance = 0

sol_mint = "So11111111111111111111111111111111111111112"
usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def performSwap(sent_amount, sent_token_mint, sol_price):

    if (sent_token_mint == sol_mint):
        usdc_balance = sent_amount * sol_price
        sol_balance = sol_balance - sent_amount
    else:
        usdc_balance = usdc_balance - sent_amount
        sol_balance = sent_amount / sol_price