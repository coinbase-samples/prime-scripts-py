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
parser = argparse.ArgumentParser(description='Request to unstake currency across a portfolio')
parser.add_argument('--currency-symbol', type=str, required=True, help='Currency symbol to unstake (e.g., ETH)')
parser.add_argument('--amount', type=str, required=True, help='Quantity to unstake')
parser.add_argument('--external-id', type=str, help='Custom identifier (up to 255 characters)')

args = parser.parse_args()

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/staking/unstake'

url_path = urlparse(uri).path
timestamp = str(int(time.time()))

payload = {
    'idempotency_key': str(uuid.uuid4()),
    'currency_symbol': args.currency_symbol,
    'amount': args.amount
}

if args.external_id:
    payload['metadata'] = {
        'external_id': args.external_id
    }

payload_json = json.dumps(payload)
message = timestamp + 'POST' + url_path + payload_json
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.post(uri, headers=headers, data=payload_json)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
