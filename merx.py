import wallet
import trading
import time

# Variable used to store the current functionality of Merx
can_run = None

# Prints information about Merx and the connected wallet
print("""
 __    __     ______     ______     __  __    
/\ "-./  \   /\  ___\   /\  == \   /\_\_\_\   
\ \ \-./\ \  \ \  __\   \ \  __<   \/_/\_\/_  
 \ \_\ \ \_\  \ \_____\  \ \_\ \_\   /\_\/\_\ 
  \/_/  \/_/   \/_____/   \/_/ /_/   \/_/\/_/ 
""")
print("Version 0.0.1")
can_run = wallet.checkJSONState()

# Error catching in case the program is unable to find the properties of the wallet
try:
    print("Your wallet is currently holding " + str(wallet.findSolBalance()) + " SOL and " + str(wallet.findUSDCBalance()) + " USDC.")
except:
    print("Merx was unable to find wallet values for the given conditions.")

# Function called depending on whether Merx can run properly
def merxPrompt():
    print("Would you like to initialize Merx? Please answer yes or no.")
    prompt = input()
    if (prompt.lower() == "yes" or prompt.lower() == "y"):
        trading.startTrading()
    elif (prompt.lower() == "no" or prompt.lower() == "n"):
        print("Merx will now shut down.")
        exit()
    else:
        merxPrompt()

# Checks if the run prompt should be displayed
if (can_run == True):
    merxPrompt()
else:
    exit()