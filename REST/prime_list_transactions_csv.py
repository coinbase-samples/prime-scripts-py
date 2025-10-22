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
import base64
import csv
import hashlib
import hmac
import os
import time
from urllib.parse import urlparse

import requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')
BASE_URI = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/transactions'

def get_signature(timestamp, method, path):
    message = timestamp + method + path
    return base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

def get_headers(path, timestamp):
    return {
        'X-CB-ACCESS-SIGNATURE': get_signature(timestamp, 'GET', path),
        'X-CB-ACCESS-TIMESTAMP': timestamp,
        'X-CB-ACCESS-KEY': API_KEY,
        'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
        'Accept': 'application/json'
    }

def fetch_transactions():
    all_transactions = []
    next_cursor = None

    while True:
        uri = BASE_URI
        if next_cursor:
            uri += f"?cursor={next_cursor}"

        path = urlparse(BASE_URI).path
        timestamp = str(int(time.time()))
        headers = get_headers(path, timestamp)

        response = requests.get(uri, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch: {response.text}")

        data = response.json()
        transactions = data.get("transactions", [])
        all_transactions.extend(transactions)

        pagination = data.get("pagination", {})
        next_cursor = pagination.get("next_cursor")
        if not pagination.get("has_next"):
            break

    return all_transactions

def write_to_csv(transactions, filename="transactions.csv"):
    if not transactions:
        print("No transactions to write.")
        return

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=transactions[0].keys())
        writer.writeheader()
        for tx in transactions:
            writer.writerow(tx)

if __name__ == "__main__":
    txs = fetch_transactions()
    write_to_csv(txs)
    print(f"Exported {len(txs)} transactions to transactions.csv")
