# Copyright 2025-present Coinbase Global, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from urllib.parse import urlparse

import requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Create an onchain blockchain transaction')
parser.add_argument('--wallet-id', type=str, required=True, help='Wallet ID')
parser.add_argument('--raw-txn', type=str, required=True, help='Raw unsigned transaction hex (supports EVM and Solana)')
parser.add_argument('--skip-broadcast', action='store_true', help='Skip broadcasting the transaction')
parser.add_argument('--rpc-url', type=str, help='Custom RPC URL')
parser.add_argument('--chain-id', type=str, help='EVM chain ID (required for EVM transactions)')
parser.add_argument('--network-name', type=str, help='Network name (required for EVM transactions, e.g., ethereum-mainnet, base-mainnet)')
parser.add_argument('--disable-dynamic-gas', action='store_true', help='Disable dynamic gas pricing')
parser.add_argument('--disable-dynamic-nonce', action='store_true', help='Disable dynamic nonce')
parser.add_argument('--replaced-txn-id', type=str, help='Transaction ID being replaced')

args = parser.parse_args()

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/wallets/{args.wallet_id}/onchain_transaction'
timestamp = str(int(time.time()))

payload = {
    'raw_unsigned_txn': args.raw_txn,
    'rpc': {
        'skip_broadcast': args.skip_broadcast
    }
}

# Add optional RPC URL
if args.rpc_url:
    payload['rpc']['url'] = args.rpc_url

# Add EVM parameters if chain_id or network_name provided
if args.chain_id or args.network_name or args.disable_dynamic_gas or args.disable_dynamic_nonce or args.replaced_txn_id:
    payload['evm_params'] = {}
    if args.chain_id:
        payload['evm_params']['chain_id'] = args.chain_id
    if args.network_name:
        payload['evm_params']['network_name'] = args.network_name
    if args.disable_dynamic_gas:
        payload['evm_params']['disable_dynamic_gas'] = True
    if args.disable_dynamic_nonce:
        payload['evm_params']['disable_dynamic_nonce'] = True
    if args.replaced_txn_id:
        payload['evm_params']['replaced_transaction_id'] = args.replaced_txn_id

url_path = urlparse(uri).path
message = timestamp + 'POST' + url_path + json.dumps(payload)
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

response = requests.post(uri, json=payload, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
