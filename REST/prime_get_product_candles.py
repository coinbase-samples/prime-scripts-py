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
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------
# Argument Parsing
# Example usage:
#   python prime_get_product_candles.py --product BTC-USD --granularity ONE_DAY --start 2024-08-30T00:00:00Z --end 2025-08-01T00:00:00Z
#   python prime_get_product_candles.py --product ETH-USD --granularity ONE_HOUR --hours 24
# ------------------------------------------------------------------------------

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Get product candles data')
parser.add_argument('--product', type=str, required=True, help='Product ID (e.g., BTC-USD, ETH-USD)')
parser.add_argument('--granularity', type=str, default='ONE_HOUR',
                    choices=['ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'THIRTY_MINUTE',
                             'ONE_HOUR', 'TWO_HOUR', 'SIX_HOUR', 'ONE_DAY'],
                    help='Candle granularity (default: ONE_HOUR)')
parser.add_argument('--start', type=str, help='Start time (ISO 8601 format, e.g., 2024-08-30T00:00:00Z)')
parser.add_argument('--end', type=str, help='End time (ISO 8601 format, e.g., 2025-08-01T00:00:00Z)')
parser.add_argument('--hours', type=int, help='Hours of historical data (alternative to --start/--end)')

args = parser.parse_args()

# Determine start and end timestamps
if args.hours:
    end_timestamp = datetime.now().isoformat() + 'Z'
    start_timestamp = (datetime.now() - timedelta(hours=args.hours)).isoformat() + 'Z'
elif args.start and args.end:
    start_timestamp = args.start
    end_timestamp = args.end
else:
    parser.error('Either --hours or both --start and --end must be provided')

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/candles?product_id={args.product}&granularity={args.granularity}&start_time={start_timestamp}&end_time={end_timestamp}'

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
