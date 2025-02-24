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
import sys
import json
import time
import uuid
import hmac
import base64
import hashlib
import requests
import argparse
from urllib.parse import urlparse

# ------------------------------------------------------------------------------
#  Command-line arguments
#  Usage example:
#     python script.py --product ETH-USD --side BUY --size 0.004 --limit 3000
# ------------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Create and accept an RFQ or place an order based on comparison with the CLOB."
)
parser.add_argument("--product", required=True, help="Product pair, e.g. ETH-USD")
parser.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Trade side (BUY or SELL)")
parser.add_argument("--size", required=True, help="Base quantity to trade, e.g. 0.004")
parser.add_argument("--limit", required=True, help="Limit price, e.g. 3000")
args = parser.parse_args()

product_id = args.product
side = args.side
base_quantity = args.size
limit_price = args.limit

# ------------------------------------------------------------------------------
#  Environment variables for authentication
# ------------------------------------------------------------------------------
API_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SIGNING_KEY")
PASSPHRASE = os.environ.get("PASSPHRASE")
PORTFOLIO_ID = os.environ.get("PORTFOLIO_ID")

def sign_payload(timestamp, method, path, body):
    message = timestamp + method + path + json.dumps(body)
    signature = hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(signature)

# ------------------------------------------------------------------------------
#  1) Create an Order Preview (CLOB)
# ------------------------------------------------------------------------------
client_order_id = str(uuid.uuid4())
preview_uri = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order_preview"
preview_timestamp = str(int(time.time()))

preview_payload = {
    "portfolio_id": PORTFOLIO_ID,
    "product_id": product_id,
    "side": side,
    "type": "LIMIT",
    "limit_price": limit_price,
    "base_quantity": base_quantity,
}

preview_path = urlparse(preview_uri).path
preview_signature_b64 = sign_payload(preview_timestamp, "POST", preview_path, preview_payload)

preview_headers = {
    "X-CB-ACCESS-SIGNATURE": preview_signature_b64,
    "X-CB-ACCESS-TIMESTAMP": preview_timestamp,
    "X-CB-ACCESS-KEY": API_KEY,
    "X-CB-ACCESS-PASSPHRASE": PASSPHRASE,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

print("=== Creating Order Preview (CLOB) ===")
preview_res = requests.post(preview_uri, json=preview_payload, headers=preview_headers)
preview_parsed = preview_res.json()
print(json.dumps(preview_parsed, indent=3))

clob_avg_fill_price = float(preview_parsed.get("average_filled_price", 0.0))

# ------------------------------------------------------------------------------
#  2) Create an RFQ
# ------------------------------------------------------------------------------
rfq_uri = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/rfq"
rfq_timestamp = str(int(time.time()))
rfq_client_quote_id = str(uuid.uuid4())

rfq_payload = {
    "portfolio_id": PORTFOLIO_ID,
    "product_id": product_id,
    "client_quote_id": rfq_client_quote_id,
    "side": side,
    "limit_price": limit_price,
    "type": "RFQ",
    "base_quantity": base_quantity,
}

rfq_path = urlparse(rfq_uri).path
rfq_signature_b64 = sign_payload(rfq_timestamp, "POST", rfq_path, rfq_payload)

rfq_headers = {
    "X-CB-ACCESS-SIGNATURE": rfq_signature_b64,
    "X-CB-ACCESS-TIMESTAMP": rfq_timestamp,
    "X-CB-ACCESS-KEY": API_KEY,
    "X-CB-ACCESS-PASSPHRASE": PASSPHRASE,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

print("\n=== Creating RFQ ===")
rfq_res = requests.post(rfq_uri, json=rfq_payload, headers=rfq_headers)
rfq_parsed = rfq_res.json()
print(json.dumps(rfq_parsed, indent=3))

quote_id = rfq_parsed.get("quote_id", "")
rfq_best_price = float(rfq_parsed.get("best_price", 0.0))

# ------------------------------------------------------------------------------
#  3) Compare prices (For BUY: lower is better; for SELL: higher is better)
# ------------------------------------------------------------------------------
print("\n=== Comparison ===")
print(f"RFQ best_price: {rfq_best_price}")
print(f"CLOB average_filled_price: {clob_avg_fill_price}")

def is_rfq_better(side_str, rfq_price, clob_price):
    if side_str.upper() == "BUY":
        return rfq_price < clob_price
    elif side_str.upper() == "SELL":
        return rfq_price > clob_price
    else:
        raise ValueError("Side must be 'BUY' or 'SELL'")

rfq_is_better = is_rfq_better(side, rfq_best_price, clob_avg_fill_price)

# ------------------------------------------------------------------------------
#  4) If RFQ is better -> Accept the quote; else -> Place a real order
# ------------------------------------------------------------------------------
if rfq_is_better:
    print("RFQ is better than CLOB price. Accepting the quote...")
    time.sleep(0.5)

    accept_uri = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/accept_quote"
    accept_timestamp = str(int(time.time()))
    accept_payload = {
        "portfolio_id": PORTFOLIO_ID,
        "product_id": product_id,
        "side": side,
        "client_order_id": client_order_id,  # or generate new
        "quote_id": quote_id,
    }

    accept_path = urlparse(accept_uri).path
    accept_signature_b64 = sign_payload(accept_timestamp, "POST", accept_path, accept_payload)

    accept_headers = {
        "X-CB-ACCESS-SIGNATURE": accept_signature_b64,
        "X-CB-ACCESS-TIMESTAMP": accept_timestamp,
        "X-CB-ACCESS-KEY": API_KEY,
        "X-CB-ACCESS-PASSPHRASE": PASSPHRASE,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    accept_res = requests.post(accept_uri, json=accept_payload, headers=accept_headers)
    accept_parsed = accept_res.json()

    print("\n=== Accept Quote Response ===")
    print(json.dumps(accept_parsed, indent=3))
    print(f"HTTP Status: {accept_res.status_code}")
else:
    print("CLOB is better or equal. Placing a real LIMIT order on the CLOB...")

    order_uri = f"https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/order"
    order_timestamp = str(int(time.time()))
    actual_client_order_id = str(uuid.uuid4())

    order_payload = {
        "portfolio_id": PORTFOLIO_ID,
        "product_id": product_id,
        "side": side,
        "type": "LIMIT",
        "limit_price": limit_price,
        "base_quantity": base_quantity,
        "client_order_id": actual_client_order_id
    }

    order_path = urlparse(order_uri).path
    order_signature_b64 = sign_payload(order_timestamp, "POST", order_path, order_payload)

    order_headers = {
        "X-CB-ACCESS-SIGNATURE": order_signature_b64,
        "X-CB-ACCESS-TIMESTAMP": order_timestamp,
        "X-CB-ACCESS-KEY": API_KEY,
        "X-CB-ACCESS-PASSPHRASE": PASSPHRASE,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    order_res = requests.post(order_uri, json=order_payload, headers=order_headers)
    order_parsed = order_res.json()

    print("\n=== Place Order Response ===")
    print(json.dumps(order_parsed, indent=3))
    print(f"HTTP Status: {order_res.status_code}")
