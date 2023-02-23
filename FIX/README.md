# FIX README.md

This is a Python FIX API test suite for Coinbase's Prime FIX APIs. 

# Getting started

## 1. Getting into the FIX directory

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

You will need to install two dependencies for this to operate: quickfix and certifi. This allows for Python to successfully connect to Coinbase via FIX. This can be done with the following command:

```
pip install -r requirements.txt
```

We also want to store and grab variables to ensure that you can connect to Prime via FIX. Run the following to declare these variables:

```bash

export ACCESS_KEY=ACCESSKEYHERE
export PASSPHRASE=PASSPHRASEHERE
export SIGNING_KEY=SIGNING_KEYHERE
export PORTFOLIO_ID=PORTFOLIO_IDHERE
export SVC_ACCOUNTID=SVC_ACCOUNTIDHERE
export FIX_VERSION=FIX.4.2
export TARGET_COMP_ID=COIN
```

Connect to FIX with any of the `client_*` scripts, e.g.:

```
python client_create_order.py
```