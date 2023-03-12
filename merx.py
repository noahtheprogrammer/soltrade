from merx import wallet
from merx import trading

# Variable used to store the current functionality of Merx
can_run = None

# Prints "Merx" and information about the connected wallet
print(""" ________   ___ ______  __
|  _   _ \ / _ \  __\ \/ /
| | | | | |  __/ |   >  < 
|_| |_| |_|\___|_|  /_/\_\ 
""")
can_run = wallet.check_json_state()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print(f"Merx has detected {wallet.find_usdc_balance()} $USDC tokens available for trading.")
except:
    print("Merx was unable to find the wallet balance for the specified parameters.")
    exit()

# Function called depending on whether Merx can run properly
def merx_prompt():
    print("Would you like to initialize Merx?")
    prompt = input()
    if (prompt.lower() == "yes" or prompt.lower() == "y"):
        trading.start_trading()
    elif (prompt.lower() == "no" or prompt.lower() == "n"):
        print("Merx has now been shut down.")
        exit()
    else:
        merx_prompt()

# Checks if the run prompt should be displayed
if (can_run == True):
    merx_prompt()
else:
    exit()