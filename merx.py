import wallet
import trading
import time

print("""
 __    __     ______     ______     __  __    
/\ "-./  \   /\  ___\   /\  == \   /\_\_\_\   
\ \ \-./\ \  \ \  __\   \ \  __<   \/_/\_\/_  
 \ \_\ \ \_\  \ \_____\  \ \_\ \_\   /\_\/\_\ 
  \/_/  \/_/   \/_____/   \/_/ /_/   \/_/\/_/ 
""")
print("Version 0.0.1")
time.sleep(1)
wallet.checkJSONState()
time.sleep(1)
print("Your wallet currently is holding " + str(wallet.findSolBalance()) + " SOL and " + str(wallet.findUSDCBalance()) + " USDC tokens.")
time.sleep(2)
def merxPrompt():
    print("Would you like to initialize Merx? Please answer yes or no.")
    prompt = input()
    if (prompt.lower() == "yes"):
        trading.startTrading()
    elif (prompt.lower() == "no"):
        print("Merx will now shut down.")
        time.sleep(2)
        exit()
    else:
        merxPrompt()
merxPrompt()