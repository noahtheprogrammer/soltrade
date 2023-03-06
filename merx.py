import wallet
import trading

# Variable used to store the current functionality of Merx
can_run = None

# Prints "Merx" and information about the connected wallet
print("""                        
 ________   ___ ______  __
|  _   _ \ / _ \  __\ \/ /
| | | | | |  __/ |   >  < 
|_| |_| |_|\___|_|  /_/\_\
                                            
""")
can_run = wallet.checkJSONState()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print(f"Merx has detected {wallet.findUSDCBalance()} $USDC tokens available for trading.")
except:
    print("Merx was unable to find the wallet balance for the specified parameters.")
    exit()

# Function called depending on whether Merx can run properly
def merxPrompt():
    print("Would you like to initialize Merx?")
    prompt = input()
    if (prompt.lower() == "yes" or prompt.lower() == "y"):
        trading.startTrading()
    elif (prompt.lower() == "no" or prompt.lower() == "n"):
        print("Merx has now been shut down.")
        exit()
    else:
        merxPrompt()

# Checks if the run prompt should be displayed
if (can_run == True):
    merxPrompt()
else:
    exit()