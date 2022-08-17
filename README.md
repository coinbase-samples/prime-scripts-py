# Purpose

The Prime Workshop Scripts repository is a collection of Python scripts meant to be used alongside the Coinbase Prime Workshop. These scripts cover common REST endpoints and WebSocket connections used in an introducing brokers-style integration with Prime APIs.

Prime workshop link here: [https://prime.saworkshop.dev/](https://prime.saworkshop.dev/)

All scripts are written in Python3 and have been tested with versions that are not end of life.

## Installation

Simply clone the repo to run scripts from your command line.

```bash
git clone https://github.com/jc-cb/prime-workshop-scripts
```

The workshop itself details all dependencies you will need to install. However, if you are viewing this as a standalone, there are a few dependencies you'll need to install, as well as set several environmental variables:

```
pip install -r requirements.txt

export ACCESS_KEY=ACCESS_KEY_HERE
export PASSPHRASE=PASSPHRASE_HERE
export SIGNING_KEY=SIGNING_KEY_HERE
export PORTFOLIO_ID=PORTFOLIO_ID_HERE
export ORIGIN_WALLET_ID=ORIGIN_WALLET_ID_HERE
export SVC_ACCOUNTID=SVC_ACCOUNTID_HERE
export WALLET_NAME=WALLET_NAME_HERE
export ADDRESS_NAME=$WALLET_NAME-external
export BLOCKCHAIN_ADDRESS=0x000000000000000000000000000000$(date +"%s")
echo "export PASSPHRASE='$PASSPHRASE'" >> ~/.bash_profile
echo "export ACCESS_KEY='$ACCESS_KEY'" >> ~/.bash_profile
echo "export SIGNING_KEY='$SIGNING_KEY'" >> ~/.bash_profile
echo "export PORTFOLIO_ID='$PORTFOLIO_ID'" >> ~/.bash_profile
echo "export ORIGIN_WALLET_ID='$ORIGIN_WALLET_ID'" >> ~/.bash_profile
echo "export SVC_ACCOUNTID='$SVC_ACCOUNTID'" >> ~/.bash_profile
echo "export WALLET_NAME='$WALLET_NAME'" >> ~/.bash_profile
echo "export ADDRESS_NAME='ADDRESS_NAME'" >> ~/.bash_profile
echo "export BLOCKCHAIN_ADDRESS='$BLOCKCHAIN_ADDRESS'" >> ~/.bash_profile
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
