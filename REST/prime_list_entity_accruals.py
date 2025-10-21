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

# Parse command line arguments
parser = argparse.ArgumentParser(description='List interest accruals for an entity')
parser.add_argument('--portfolio-id', type=str, required=True, help='The unique ID of the portfolio')
parser.add_argument('--start-date', type=str, required=True, help='Start date in RFC3339 format')
parser.add_argument('--end-date', type=str, required=True, help='End date in RFC3339 format')

args = parser.parse_args()

# Build query string
query_params = [
    f'portfolio_id={args.portfolio_id}',
    f'start_date={args.start_date}',
    f'end_date={args.end_date}'
]

uri = f'https://api.prime.coinbase.com/v1/entities/{ENTITY_ID}/accruals?{"&".join(query_params)}'
url_path = urlparse(uri).path
timestamp = str(int(time.time()))
message = timestamp + 'GET' + url_path
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

response = requests.get(uri, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
