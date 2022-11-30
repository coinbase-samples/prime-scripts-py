# FIX README.md

This is a Python FIX API test suite for Coinbase's Prime FIX APIs. 
## Workshop Tutorial

# Getting started

## 1. Getting into the FIX directory

This first step will differ depending on if your workshop covers a combination of REST and FIX or exclusively FIX.

If you are currently in the REST directory, you can use the following command: 
```
cd ~/environment/prime-scripts-py/FIX
```
If you did **not** participate in the REST workshop and are only participating in the FIX workshop, you need to clone the repository and then navigate into the FIX repository with these two commands:
```
git clone https://github.com/coinbase-samples/prime-scripts-py
cd prime-scripts-py/FIX
```

## 2. Configuration

1. You will need to install two dependencies for this to operate: quickfix and certifi. This allows for FIX to run within Python. This can be done with the following command:

```
pip install -r requirements.txt
```

2. When connecting to Coinbase Prime via FIX, you will need to provide your API credentials and portfolio ID. This can be accomplished by running the following command:

```
sed -i "s,YOUR_API_PASSPHRASE,$PASSPHRASE," fix/resources/prime.properties
sed -i "s,YOUR_API_KEY,$ACCESS_KEY," fix/resources/prime.properties
sed -i "s,YOUR_API_SECRET,$SIGNING_KEY," fix/resources/prime.properties
sed -i "s,YOUR_PORTFOLIO_ID,$PORTFOLIO_ID," fix/resources/prime.properties
sed -i "s,YOUR_SVC_ACCOUNT_ID,$SVC_ACCOUNTID," fix/resources/prime.properties
```

## 3. Running Your FIX Application

1. To begin the FIX workshop, run the following command: 
```
python client.py
```

2. In your Run Console you should see a menu prompting you to enter 1-4 to explore.

```
Please choose one of the following: 
1: Place New Order
2: Get Order Status
3: Cancel Order
4: Exit Application!
```

