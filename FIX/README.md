# tam-prime-fix-api

## Overview

TAM Prime FIX API Test Suite

This Repository is a Python FIX API Test Suite for Coinbase's Prime FIX APIs.  This Repository is
designed for API testing & learning.

## 1. Clone the Github Repository and Open the Project in Pycharm

1. Clone the repo using the following command from your Terminal window: 
```
git clone https://github.com/coinbase-samples/prime-scripts-py
```

2. Open project in IDE of your choice or navigate to the following folder directory from Terminal:  
```
cd prime-scripts-py/FIX
```

## 2.  Configuration

1. You will need to install a single dependency for this to operate: quickfix. This allows for FIX to run within Python. This can be done with the following command: 
    
```
pip install quickfix-ssl
```

2. If you are participating in a Coinbase Prime workshop for FIX, you may skip this step. If you are visiting our samples repository, you will need to generate these credentials yourself and place them over the values below (e.g. ACCESS_KEY_HERE), then run the below code:

```
export ACCESS_KEY=ACCESS_KEY_HERE
export PASSPHRASE=PASSPHRASE_HERE
export SIGNING_KEY=SIGNING_KEY_HERE
export PORTFOLIO_ID=PORTFOLIO_ID_HERE
```
3. Whether you are visiting our repository or participating in a Coinbase workshop, you will need to run the below:

```
sed -i "s/YOUR_SERVICE_ACCOUNT_ID/$SVC_ACCOUNTID/" resources/client.cfg
```

## 3.  Running Your FIX Application

1. Open the **client.py** file in Pycharm or **/FIX** folder if you are running this from the command line.
2. If using an IDE such as Pycharm, press the **'Green Play Button'** next to the **if __name__=='__main__'** function. Otherwise, run the following command:
```
python3 client.py resources/client.cfg
```
3. In your Run Console you should see a menu.  Enter 1-5 to explore
4. Navigate to your Logs folder. Open your **message.log** file to explore inbound + outbound FIX messages

## 4.  Message Types

Navigate to **model/order.py** to view and adjust the FIX order types for testing:

- Market Buy/Sell (Base)
- Market Buy/Sell (Quote)
- Limit Buy/Sell (Base)
- Order Status Request
- Cancel Order