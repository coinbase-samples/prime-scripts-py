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
from urllib.parse import urlparse

import requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Update onchain address group')
parser.add_argument('--group-id', type=str, required=True, help='Address group ID')
parser.add_argument('--name', type=str, required=True, help='Group name')
parser.add_argument('--network-type', type=str, required=True, choices=['NETWORK_TYPE_EVM', 'NETWORK_TYPE_SOLANA'], help='Network type')
parser.add_argument('--addresses', type=str, required=True, help='JSON array of address entries')
parser.add_argument('--added-at', type=str, required=True, help='Added at timestamp (ISO 8601 format)')

args = parser.parse_args()

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/onchain_address_group'

url_path = urlparse(uri).path
timestamp = str(int(time.time()))

# Parse addresses JSON
try:
    addresses = json.loads(args.addresses)
except json.JSONDecodeError:
    parser.error('--addresses must be valid JSON array')

payload = {
    'address_group': {
        'id': args.group_id,
        'name': args.name,
        'network_type': args.network_type,
        'addresses': addresses,
        'added_at': args.added_at
    }
}

payload_json = json.dumps(payload)
message = timestamp + 'PUT' + url_path + payload_json
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.put(uri, headers=headers, data=payload_json)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
