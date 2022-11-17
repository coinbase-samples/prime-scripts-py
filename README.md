# Purpose

This repository is a collection of Python scripts meant to demonstrate various REST and WebSocket APIs available for Coinbase Prime.

While originally designed to stand alongside the Coinbase Prime Workshop, these scripts will work on their own with proper API credentials. 

Prime workshop link here: [https://prime.saworkshop.dev/](https://prime.saworkshop.dev/)

All scripts are written in Python3 and have been tested with versions that are not end of life.

## Installation

Simply clone the repo to run scripts from your command line.

```bash
git clone https://github.com/coinbase-samples/prime-scripts-py
```

The two dependencies needed for these scripts are requests and websockets, in order to make REST and WebSocket requests, respectively. This can be done easily with the following command:

```
pip install -r requirements.txt
```

Finally, these scripts make use of command line environment variables so that sensitive information does not need to be included in the scripts themselves. itself details all dependencies you will need to install. However, if you are viewing this as a standalone, 
```
export ACCESS_KEY=ACCESS_KEY_HERE
export PASSPHRASE=PASSPHRASE_HERE
export SIGNING_KEY=SIGNING_KEY_HERE
export PORTFOLIO_ID=PORTFOLIO_ID_HERE
export SVC_ACCOUNTID=SVC_ACCOUNTID_HERE
```

## Contributing
Pull requests are welcome. For major changes, please open an issue to discuss what you would like to change.
