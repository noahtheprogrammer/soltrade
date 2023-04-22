<div align="center">
  <img src=https://user-images.githubusercontent.com/81941019/228043179-454302f4-fdaf-4715-92a3-f19a4c2e7ccc.png alt="merx_logo">
  <img src=https://img.shields.io/github/downloads/noahtheprogrammer/merxbot/total?style=for-the-badge alt="download_count">
  <img src=https://img.shields.io/github/contributors/noahtheprogrammer/merxbot?style=for-the-badge alt="contributor_count">
  <img src=https://img.shields.io/github/issues-raw/noahtheprogrammer/merxbot?style=for-the-badge alt="issue_count">
  <img src=https://img.shields.io/github/repo-size/noahtheprogrammer/merxbot?style=for-the-badge alt="repo_size">
</div>

### Introduction
Merx is a Python-based, open source trading bot that I created in order to dive deeper into the workings of the blockchain and leap headfirst into the world of technical analysis. It integrates EMA, RSI, and Bollinger Band indicators into a fifteen-minute interval to predict the most profitable course of action. Jupiter has been integrated into Merx as well, allowing for near-instantaneous transactions with minimal fees. Merx is fairly customizable, with more user input to come in later versions. A ten-day chart of open and close positions with Merx's algorithm can be viewed below.

<div align="center">
  <img src=https://user-images.githubusercontent.com/81941019/227742349-d87b9dab-286e-47a9-a1b7-51f4e8023274.png alt="merx_chart">
</div>

### Disclaimer
This software was created for education purposes only and, like all trading bots, cannot predict the future.
Please do not risk money you are not willing or cannot afford to lose. 
The creators and contributors of Merx are not responsible for any losses you might incur during trading.

### Installation
In order to use Merx you will need a free CryptoCompare API key and access to a wallet application such as Phantom.
Open the installation folder and create a file titled `config.json` with the following code block, replacing the placeholder values with your API key and wallet private key. Both keys are required to receive pricing data and perform trading transactions.
```
{
  "api_key": "yourapikeyhere",
  "private_key": "yourprivatekeyhere"
}
```
Next, install the dependencies for Merx by opening Python and running the following command.
This will install automatically install the required modules and their respective versions.
```
python -m pip install -r requirements.txt
```
If the Merx is unable to open after following the installation process, try restarting your machine, as Python occassionally requires a reboot in order to successfully import modules.

### Usage
Make sure you have deposited at least 1 $USDC in your connected wallet for Merx to begin trading, along with 0.1 $SOL to pay for gas.
After the installation has been completed, begin Merx by running `merx.py` on your desktop or using Python commands.
Then, use the designated inputs to pause, resume, or quit the program.

### Contributions
if you have any interest in contributing, fork the repository and submit a pull request to have your improvements merged into the main repository. When opening an issue or feature request, be sure to provide a clear title and description of the issue you are experiencing or the feature you would like to suggest. Once submitted, I will review the issue and respond as soon as possible.

### Donations
Merx does not include a platform fee and will remain free forever.
If you're feeling a bit more generous however, please donate to my $SOL address below.
```
6XeQkUDZdsGsKBrhGWRuweHu4nbcv23t8r8vPt5xEsMv
```
