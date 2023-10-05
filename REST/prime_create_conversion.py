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

from urllib.parse import urlparse
import json, hmac, hashlib, time, uuid, os, base64, requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

wallet_id = 'WALLET_UUID'

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/wallets/{wallet_id}/conversion'

timestamp = str(int(time.time()))
method = 'POST'

# this endpoint only supports conversions between USDC and USD
amount = '1'
destination = 'DESTINATION_WALLET_UUID'
idempotency_key = uuid.uuid4()
source_symbol = 'USD'
destination_symbol = 'USDC'


payload = {
    'portfolio_id': PORTFOLIO_ID,
    'wallet_id': wallet_id,
    'amount': amount,
    'destination': destination,
    'idempotency_key': str(idempotency_key),
    'source_symbol': source_symbol,
    'destination_symbol': destination_symbol
}

url_path = urlparse(uri).path
message = timestamp + method + url_path + json.dumps(payload)
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-timestamp': timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

response = requests.request(method, uri, json=payload, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))