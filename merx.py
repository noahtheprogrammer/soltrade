from merx.wallet import *
from merx.trading import *
from merx.text import colors, timestamp

# Prints "Merx" and information about the connected wallet
print(""" ________   ___ ______  __
|  _   _ \ / _ \  __\ \/ /
| | | | | |  __/ |   >  < 
|_| |_| |_|\___|_|  /_/\_\ """)
can_run = check_json_state()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print(timestamp.TIME + f": Merx has detected {find_usdc_balance()} $USDC tokens available for trading.")
except:
    print(colors.WARNING + timestamp.TIME + ": Merx was unable to find $USDC tokens available for trading at this time." + colors.ENDC)
    exit()

# Checks if the run prompt should be displayed
if (can_run):
    start_trading()
else:
    exit()