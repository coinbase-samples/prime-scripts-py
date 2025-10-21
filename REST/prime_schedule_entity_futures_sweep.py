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

import os
import json
import hmac
import hashlib
import time
import base64
import requests
import argparse
from urllib.parse import urlparse

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
ENTITY_ID = os.environ.get('ENTITY_ID')

parser = argparse.ArgumentParser(description='Schedule entity futures sweep from FCM wallet to USD Spot wallet')
parser.add_argument('--currency', type=str, required=True, help='Currency symbol (e.g. USD)')
parser.add_argument('--amount', type=str, help='Amount to sweep (optional - defaults to sweep all if not provided)')

args = parser.parse_args()

uri = f'https://api.prime.coinbase.com/v1/entities/{ENTITY_ID}/futures/sweeps'

url_path = urlparse(uri).path
timestamp = str(int(time.time()))

payload = {
    'currency': args.currency
}

if args.amount:
    payload['amount'] = args.amount

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
