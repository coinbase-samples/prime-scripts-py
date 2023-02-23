# Copyright 2023 Coinbase Global, Inc.
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

import json, hmac, hashlib, time, uuid, os, base64, requests
from urllib.parse import urlparse

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')
WALLET_NAME = os.environ.get('WALLET_NAME')

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/wallets?type=VAULT&symbols=ETH'
timestamp = str(int(time.time()))
idempotency_key = uuid.uuid4()
method = 'GET'

url_path = urlparse(uri).path
message = timestamp + method + url_path
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
   'X-CB-ACCESS-SIGNATURE': signature_b64,
   'X-CB-ACCESS-timestamp': timestamp,
   'X-CB-ACCESS-KEY': API_KEY,
   'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
   'Accept': 'application/json'
}
response = requests.get(uri, headers=headers)
parsed_response = json.loads(response.text)
wallets = parsed_response['wallets']

for wallet in wallets:
    if wallet['name'] == WALLET_NAME:
        destination_wallet_id = wallet['id']
        print(destination_wallet_id)
