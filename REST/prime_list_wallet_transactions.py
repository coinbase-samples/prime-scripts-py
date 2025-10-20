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

# ------------------------------------------------------------------------------
# Argument Parsing
# Example usage:
#   python prime_list_wallet_transactions.py --wallet-id abc123 --types DEPOSIT
#   python prime_list_wallet_transactions.py --wallet-id abc123 --types WITHDRAWAL --limit 100
#   python prime_list_wallet_transactions.py --wallet-id abc123 --types DEPOSIT,WITHDRAWAL
# ------------------------------------------------------------------------------

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

# Parse command line arguments
parser = argparse.ArgumentParser(description='List wallet transactions')
parser.add_argument('--wallet-id', type=str, required=True, help='Wallet ID')
parser.add_argument('--types', type=str, help='Transaction types (comma-separated, e.g., DEPOSIT,WITHDRAWAL)')
parser.add_argument('--limit', type=int, default=100, help='Maximum number of transactions to return (default: 100)')

args = parser.parse_args()

# Build URI with query parameters
query_params = f'limit={args.limit}'
if args.types:
    query_params += f'&types={args.types}'

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/wallets/{args.wallet_id}/transactions?{query_params}'
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
