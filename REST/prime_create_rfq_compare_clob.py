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

import json
import hmac
import hashlib
import time
import uuid
import os
import base64
import requests
from urllib.parse import urlparse


API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

client_order_id = str(uuid.uuid4())

product_id = 'ETH-USD'
side = 'BUY'
base_quantity = '0.004'
limit_price = '3000'

# ------------------------------------------------------------------------------
# 1) Create an Order Preview against the CLOB
# ------------------------------------------------------------------------------
preview_uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order_preview'
preview_timestamp = str(int(time.time()))

preview_payload = {
    'portfolio_id': PORTFOLIO_ID,
    'product_id': product_id,
    'side': side,
    'type': 'LIMIT',
    'limit_price': limit_price,
    'base_quantity': base_quantity
}

preview_url_path = urlparse(preview_uri).path
preview_message = preview_timestamp + 'POST' + preview_url_path + json.dumps(preview_payload)
preview_signature_b64 = base64.b64encode(
    hmac.digest(SECRET_KEY.encode(), preview_message.encode(), hashlib.sha256)
)

preview_headers = {
    'X-CB-ACCESS-SIGNATURE': preview_signature_b64,
    'X-CB-ACCESS-TIMESTAMP': preview_timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

preview_response = requests.post(preview_uri, json=preview_payload, headers=preview_headers)
preview_parsed = preview_response.json()

print("=== Order Preview (CLOB) ===")
print(json.dumps(preview_parsed, indent=3))

clob_avg_fill_price = float(preview_parsed.get('average_filled_price', 0.0))

# ------------------------------------------------------------------------------
# 2) Create an RFQ
# ------------------------------------------------------------------------------
rfq_uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/rfq'
rfq_timestamp = str(int(time.time()))
rfq_client_quote_id = str(uuid.uuid4())

rfq_payload = {
    'portfolio_id': PORTFOLIO_ID,
    'product_id': product_id,
    'client_quote_id': rfq_client_quote_id,
    'side': side,
    'limit_price': limit_price,
    'type': 'RFQ',
    'base_quantity': base_quantity
}

rfq_url_path = urlparse(rfq_uri).path
rfq_message = rfq_timestamp + 'POST' + rfq_url_path + json.dumps(rfq_payload)
rfq_signature_b64 = base64.b64encode(
    hmac.digest(SECRET_KEY.encode(), rfq_message.encode(), hashlib.sha256)
)

rfq_headers = {
    'X-CB-ACCESS-SIGNATURE': rfq_signature_b64,
    'X-CB-ACCESS-TIMESTAMP': rfq_timestamp,
    'X-CB-ACCESS-KEY': API_KEY,
    'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
    'Accept': 'application/json'
}

rfq_response = requests.post(rfq_uri, json=rfq_payload, headers=rfq_headers)
rfq_parsed = rfq_response.json()

print("\n=== RFQ Response ===")
print(json.dumps(rfq_parsed, indent=3))

quote_id = rfq_parsed.get("quote_id", "")
rfq_best_price = float(rfq_parsed.get("best_price", 0.0))

# ------------------------------------------------------------------------------
# 3) Compare RFQ best_price vs. CLOB average_filled_price
#    (For a BUY, lower is better; for a SELL, higher is better)
# ------------------------------------------------------------------------------
print("\n=== Comparison ===")
print(f"RFQ best_price: {rfq_best_price}")
print(f"CLOB average_filled_price: {clob_avg_fill_price}")

def is_rfq_better(side, rfq_price, clob_price):
    if side.upper() == 'BUY':
        return rfq_price < clob_price
    elif side.upper() == 'SELL':
        return rfq_price > clob_price
    else:
        raise ValueError("Side must be 'BUY' or 'SELL'")

rfq_is_better = is_rfq_better(side, rfq_best_price, clob_avg_fill_price)

# ------------------------------------------------------------------------------
# 4) If RFQ is better -> Accept the RFQ; else -> Place an actual order
# ------------------------------------------------------------------------------
if rfq_is_better:
    print("RFQ is better than CLOB price. Accepting the quote...")

    time.sleep(0.5)  # small pause

    accept_uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/accept_quote'
    accept_timestamp = str(int(time.time()))
    accept_payload = {
        'portfolio_id': PORTFOLIO_ID,
        'product_id': product_id,
        'side': side,
        'client_order_id': client_order_id,
        'quote_id': quote_id
    }

    accept_url_path = urlparse(accept_uri).path
    accept_message = accept_timestamp + 'POST' + accept_url_path + json.dumps(accept_payload)
    accept_signature_b64 = base64.b64encode(
        hmac.digest(SECRET_KEY.encode(), accept_message.encode(), hashlib.sha256)
    )

    accept_headers = {
        'X-CB-ACCESS-SIGNATURE': accept_signature_b64,
        'X-CB-ACCESS-TIMESTAMP': accept_timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    accept_response = requests.post(accept_uri, json=accept_payload, headers=accept_headers)
    accept_parsed = accept_response.json()

    print("\n=== Accept Quote Response ===")
    print(json.dumps(accept_parsed, indent=3))
    print(f"HTTP Status: {accept_response.status_code}")

else:
    print("CLOB is better or equal. Placing a real LIMIT order on the CLOB...")

    order_uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order'
    order_timestamp = str(int(time.time()))
    client_order_id = str(uuid.uuid4())

    order_payload = {
        'portfolio_id': PORTFOLIO_ID,
        'product_id': product_id,
        'side': side,
        'type': 'LIMIT',
        'limit_price': limit_price,
        'base_quantity': base_quantity,
        'client_order_id': client_order_id
    }

    order_url_path = urlparse(order_uri).path
    order_message = order_timestamp + 'POST' + order_url_path + json.dumps(order_payload)
    order_signature_b64 = base64.b64encode(
        hmac.digest(SECRET_KEY.encode(), order_message.encode(), hashlib.sha256)
    )

    order_headers = {
        'X-CB-ACCESS-SIGNATURE': order_signature_b64,
        'X-CB-ACCESS-TIMESTAMP': order_timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    order_response = requests.post(order_uri, json=order_payload, headers=order_headers)
    order_parsed = order_response.json()

    print("\n=== Place Order Response ===")
    print(json.dumps(order_parsed, indent=3))
    print(f"HTTP Status: {order_response.status_code}")
