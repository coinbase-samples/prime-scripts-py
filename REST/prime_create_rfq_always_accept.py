# Copyright 2025-present Coinbase Global, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
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
import time
import uuid
import hmac
import hashlib
import base64
import requests
from urllib.parse import urlparse

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

def sign_headers(method: str, url: str, payload: dict) -> dict:
    timestamp = str(int(time.time()))
    url_path = urlparse(url).path
    message = timestamp + method.upper() + url_path + json.dumps(payload)
    signature = base64.b64encode(
        hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256)
    )
    return {
        'X-CB-ACCESS-SIGNATURE': signature,
        'X-CB-ACCESS-TIMESTAMP': timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

# ------------------------------
# 1) Create an RFQ
# ------------------------------
rfq_url = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/rfq'
client_quote_id = str(uuid.uuid4())

product_id = 'SOL-USD'
side = 'BUY'
order_type = 'RFQ'
limit_price = '350'
base_quantity = '0.5'

rfq_payload = {
    'portfolio_id': PORTFOLIO_ID,
    'product_id': product_id,
    'client_quote_id': client_quote_id,
    'side': side,
    'limit_price': limit_price,
    'type': order_type,
    'base_quantity': base_quantity
}

headers = sign_headers('POST', rfq_url, rfq_payload)
rfq_response = requests.post(rfq_url, json=rfq_payload, headers=headers)
rfq_parsed = rfq_response.json()
print("=== RFQ Response ===")
print(json.dumps(rfq_parsed, indent=3))

quote_id = rfq_parsed["quote_id"]

# ------------------------------
# 2) Accept the Quote
# ------------------------------
time.sleep(0.5)  # brief pause
accept_url = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/accept_quote'
accept_payload = {
    'portfolio_id': PORTFOLIO_ID,
    'product_id': product_id,
    'side': side,
    'client_order_id': client_quote_id,
    'quote_id': quote_id
}

headers = sign_headers('POST', accept_url, accept_payload)
accept_response = requests.post(accept_url, json=accept_payload, headers=headers)
accept_parsed = accept_response.json()

print("\n=== Accept Quote Response ===")
print(json.dumps(accept_parsed, indent=3))
print("HTTP Status:", accept_response.status_code, accept_response.text)
