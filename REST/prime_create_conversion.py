# Copyright 2022-present Coinbase Global, Inc.
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
parser = argparse.ArgumentParser(description='Create a conversion between USD, USDC, and PYUSD')
parser.add_argument('--wallet-id', type=str, required=True, help='Source wallet ID')
parser.add_argument('--amount', type=str, required=True, help='Amount to convert')
parser.add_argument('--destination', type=str, required=True, help='Destination wallet ID')
parser.add_argument('--source-symbol', type=str, required=True, choices=['USD', 'USDC', 'PYUSD'], help='Source symbol (USD, USDC, or PYUSD)')
parser.add_argument('--destination-symbol', type=str, required=True, choices=['USD', 'USDC', 'PYUSD'], help='Destination symbol (USD, USDC, or PYUSD)')

args = parser.parse_args()

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/wallets/{args.wallet_id}/conversion'

timestamp = str(int(time.time()))
idempotency_key = str(uuid.uuid4())

payload = {
    'amount': args.amount,
    'destination': args.destination,
    'idempotency_key': idempotency_key,
    'source_symbol': args.source_symbol,
    'destination_symbol': args.destination_symbol
}

url_path = urlparse(uri).path
message = timestamp + 'POST' + url_path + json.dumps(payload)
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.post(uri, headers=headers, data=json.dumps(payload))
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))