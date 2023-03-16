from merx.wallet import *
from merx.trading import *

# Prints "Merx" and information about the connected wallet
print(""" ________   ___ ______  __
|  _   _ \ / _ \  __\ \/ /
| | | | | |  __/ |   >  < 
|_| |_| |_|\___|_|  /_/\_\ 
""")

can_run = check_json_state()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print(f"Merx has detected {find_usdc_balance()} $USDC tokens available for trading.")
except:
    print("Merx was unable to find the wallet balance for the specified parameters.")
    exit()

# Function called depending on whether Merx can run properly
def merx_prompt():
    print("Would you like to initialize Merx?")
    prompt = input()
    if (prompt.lower() == "yes" or prompt.lower() == "y"):
        start_trading()
    elif (prompt.lower() == "no" or prompt.lower() == "n"):
        print("Merx has now been shut down.")
        exit()
    else:
        merx_prompt()

# Checks if the run prompt should be displayed
if (can_run):
    merx_prompt()
else:
    exit()