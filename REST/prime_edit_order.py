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
parser = argparse.ArgumentParser(description='Edit an existing order (beta)')
parser.add_argument('--order-id', type=str, required=True, help='Order ID to edit')
parser.add_argument('--orig-client-order-id', type=str, required=True, help='Original client order ID')
parser.add_argument('--client-order-id', type=str, help='New client order ID (auto-generated if not provided)')
parser.add_argument('--base-quantity', type=str, help='New base quantity')
parser.add_argument('--quote-value', type=str, help='New quote value')
parser.add_argument('--limit-price', type=str, help='New limit price')
parser.add_argument('--stop-price', type=str, help='New stop price')
parser.add_argument('--expiry-time', type=str, help='New expiry time (ISO 8601 format)')
parser.add_argument('--display-quote-size', type=str, help='New display quote size')
parser.add_argument('--display-base-size', type=str, help='New display base size')

args = parser.parse_args()

if not args.base_quantity and not args.quote_value:
    parser.error('Either --base-quantity or --quote-value must be provided')

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/orders/{args.order_id}/edit'

url_path = urlparse(uri).path
timestamp = str(int(time.time()))

payload = {
    'orig_client_order_id': args.orig_client_order_id,
    'client_order_id': args.client_order_id if args.client_order_id else str(uuid.uuid4())
}

if args.base_quantity:
    payload['base_quantity'] = args.base_quantity
if args.quote_value:
    payload['quote_value'] = args.quote_value
if args.limit_price:
    payload['limit_price'] = args.limit_price
if args.stop_price:
    payload['stop_price'] = args.stop_price
if args.expiry_time:
    payload['expiry_time'] = args.expiry_time
if args.display_quote_size:
    payload['display_quote_size'] = args.display_quote_size
if args.display_base_size:
    payload['display_base_size'] = args.display_base_size

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
