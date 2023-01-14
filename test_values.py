sol_balance = 100
usdc_balance = 0

sol_mint = "So11111111111111111111111111111111111111112"
usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def performSwap(sent_amount, sent_token_mint, sol_price):

    global sol_balance
    global usdc_balance

    if (sent_token_mint == "So11111111111111111111111111111111111111112"):
        usdc_balance = round(sent_amount * sol_price, 6)
        sol_balance = round(sol_balance - sent_amount, 9)
    else:
        usdc_balance = round(usdc_balance - sent_amount, 6)
        sol_balance = round(sent_amount / sol_price, 9)