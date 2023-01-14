import requests

# Finds the current Fear and Greed Index offered by Alternative API
def findFGI():
    response = requests.get("https://api.alternative.me/fng/")
    value = response.json()["data"][0]["value"]
    return(value)