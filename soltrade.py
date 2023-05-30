from soltrade.wallet import *
from soltrade.trading import *
from soltrade.text import colors, timestamp

# Prints "Soltrade" and information about the connected wallet
print("""                    $$\   $$\                              $$\           
                    $$ |  $$ |                             $$ |          
 $$$$$$$\  $$$$$$\  $$ |$$$$$$\    $$$$$$\  $$$$$$\   $$$$$$$ | $$$$$$\  
$$  _____|$$  __$$\ $$ |\_$$  _|  $$  __$$\ \____$$\ $$  __$$ |$$  __$$\ 
\$$$$$$\  $$ /  $$ |$$ |  $$ |    $$ |  \__|$$$$$$$ |$$ /  $$ |$$$$$$$$ |
 \____$$\ $$ |  $$ |$$ |  $$ |$$\ $$ |     $$  __$$ |$$ |  $$ |$$   ____|
$$$$$$$  |\$$$$$$  |$$ |  \$$$$  |$$ |     \$$$$$$$ |\$$$$$$$ |\$$$$$$$\ 
\_______/  \______/ \__|   \____/ \__|      \_______| \_______| \_______|
""")
can_run = check_json_state()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print(timestamp.find_time() + f": Soltrade has detected {find_usdc_balance()} $USDC tokens available for trading.")
except:
    print(colors.WARNING + timestamp.find_time() + ": Soltrade was unable to find $USDC tokens available for trading at this time." + colors.ENDC)
    exit()

# Checks if the run prompt should be displayed
if (can_run):
    print(timestamp.find_time() + ": Soltrade has successfully imported the API requirements.")
    start_trading()
else:
    exit()