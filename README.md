<div align="center">
  <img src=https://github.com/noahtheprogrammer/soltrade/assets/81941019/aee060e2-d254-447e-b2ec-746367e06483 alt="soltrade_logo">
</div>

### Introduction
Soltrade is a Python-based, open source trading bot that we created in order to dive deeper into the workings of the blockchain and leap headfirst into the world of technical analysis. It integrates EMA, RSI, and Bollinger Band indicators into a customizable trading interval to predict the most profitable course of action. Jupiter has been integrated into Soltrade as well, allowing for near-instantaneous transactions with minimal fees. Soltrade is fairly customizable, with more user input to come in later versions. A ten-day chart demonstation of open and close positions with Soltrade's algorithm can be viewed below.

<div align="center">
  <img src=https://user-images.githubusercontent.com/81941019/227742349-d87b9dab-286e-47a9-a1b7-51f4e8023274.png alt="demo_chart">
</div>

### Disclaimer
This software was created for education purposes only and, like all trading bots, cannot predict the future.
Please do not risk money you are not willing or cannot afford to lose. 
The creators and contributors of Soltrade are not responsible for any losses you might incur during trading.

### Setup
In order to use Soltrade you will need a free CryptoCompare API key and access to a wallet application such as Phantom.
Open the installation folder and create a file titled `.env` with the following code block, replacing the placeholder values with your API key and wallet private key. Both keys are required to receive pricing data and perform trading transactions.
```
API_KEY=YOUR_CRYPTOCOMPARE_KEY
WALLET_PRIVATE_KEY=YOUR_PRIVATE_KEY
SECONDARY_MINT=SECONDARY_TOKEN_ADDRESS
```
In addition to these required parameters, there are some additional ones that can be used as well.
Keep in mind that Jupiter often experiences issues when working with low slippage, so we recommend using at least a 0.5% fee or greater to minimize transaction issues. 
| Parameter                  | Description                                               | Default   |
|----------------------------|-----------------------------------------------------------|:---------:|
| `PRIMARY_MINT_SYMBOL`      | ticker symbol of main token                               |   `USD`   |
| `PRIMARY_MINT`             | token address of main currency                            | `EPjF..v` |
| `SECONDARY_MINT_SYMBOL`    | ticker symbol of custom token                             | `UNKNOWN` |
| `PRICE_UPDATE_SECONDS`     | second-based time interval between token price updates    |    `60`   |
| `TRADING_INTERVALS_MINUTE` | minute-based time interval for technical analysis         |    `1`    |
| `SLIPPAGE`                 | slippage % in BPS utilized by Jupiter during transactions |    `50`   |

### Installation
In order to install the dependencies for Soltrade, open Python and run the following command.
This will install automatically install the required modules and their respective versions.
```
python -m pip install -r requirements.txt
```
If the Soltrade is unable to open after following the installation process, try restarting your machine, as Python occassionally requires a reboot in order to successfully import modules.

Alternatively, you can install using poetry:
```
python -m pip install poetry
poetry install
```

### Docker
Build the Soltrade Docker image using the following command:
```
docker build -t soltrade_bot .
```
Once the image is built, you can run the Soltrade bot container using:
```
docker run -d --name soltrade_bot \
    -e API_KEY=<CryptoCompare API key> \
    -e WALLET_PRIVATE_KEY=<wallet_private_key> \
    -e SECOND_MINT=<token_address> \
    soltrade_bot
```
Replace <CryptoCompare API key>, <wallet_private_key>, and <token_address> with your actual values before running the command.

### Usage
Before starting Soltrade, make sure you have deposited at least 1 of the selected $TOKEN in your connected wallet, along with ~0.1 $SOL to cover any additional transaction fees.
After the installation has been completed, begin Soltrade by running `soltrade.py` on your desktop or using Python commands.
Then, use the designated inputs to pause, resume, or quit the program.

### Contributions
if you have any interest in contributing, fork the repository and submit a pull request to have your improvements merged into the main repository. When opening an issue or feature request, be sure to provide a clear title and description of the issue you are experiencing or the feature you would like to suggest. Once submitted, we will review the issue and respond as soon as possible.

### Donations
Soltrade does not currently include a platform fee and will remain open-source forever.
If you're feeling a bit more generous however, please donate to my $SOL address below.
```
6XeQkUDZdsGsKBrhGWRuweHu4nbcv23t8r8vPt5xEsMv
```
