"""
Copyright 2022 Coinbase Global, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from urllib.parse import urlparse
import json, hmac, hashlib, time, uuid, os, base64, requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

URI = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/address_book'

TIMESTAMP = str(int(time.time()))
METHOD = 'POST'

ADDRESS = os.environ.get('BLOCKCHAIN_ADDRESS')
NAME = os.environ.get('WALLET_NAME')+'_external'
SYMBOL = 'ETH'

payload = {
    'PORTFOLIO_ID': PORTFOLIO_ID,
    'address': ADDRESS,
    'currency_symbol': SYMBOL,
    'name': NAME
}

# signature and request
url_path = urlparse(URI).path
message = TIMESTAMP + METHOD + url_path + json.dumps(payload)
signature = hmac.digest(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
signature_b64 = base64.b64encode(signature)

headers = {
    'X-CB-ACCESS-SIGNATURE': signature_b64,
    'X-CB-ACCESS-TIMESTAMP': TIMESTAMP,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

response = requests.post(URI, json=payload, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response,indent=3))
