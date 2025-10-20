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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from urllib.parse import urlparse
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------
# Argument Parsing
# Example usage:
#   python prime_plot_product_candles.py --product BTC-USD --granularity ONE_HOUR --hours 350
#   python prime_plot_product_candles.py --product ETH-USD --granularity FIFTEEN_MINUTE --hours 24
# ------------------------------------------------------------------------------

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Plot candlestick chart for a product')
parser.add_argument('--product', type=str, required=True, help='Product ID (e.g., BTC-USD, ETH-USD)')
parser.add_argument('--granularity', type=str, default='ONE_HOUR',
                    choices=['ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'THIRTY_MINUTE',
                             'ONE_HOUR', 'TWO_HOUR', 'SIX_HOUR', 'ONE_DAY'],
                    help='Candle granularity (default: ONE_HOUR)')
parser.add_argument('--hours', type=int, default=350, help='Hours of historical data to fetch (default: 350)')

args = parser.parse_args()

end_time = datetime.now()
start_time = end_time - timedelta(hours=args.hours)
end_timestamp = int(end_time.timestamp())
start_timestamp = int(start_time.timestamp())

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

if 'candles' in parsed_response:
    candles = parsed_response['candles']
    
    timestamps = [datetime.fromisoformat(candle['timestamp'].replace('Z', '+00:00')) for candle in candles]
    opens = [float(candle['open']) for candle in candles]
    highs = [float(candle['high']) for candle in candles]
    lows = [float(candle['low']) for candle in candles]
    closes = [float(candle['close']) for candle in candles]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for i in range(len(timestamps)):
        color = 'green' if closes[i] >= opens[i] else 'red'
        
        ax.plot([timestamps[i], timestamps[i]], [lows[i], highs[i]], color='black', linewidth=1)
        
        body_height = abs(closes[i] - opens[i])
        body_bottom = min(opens[i], closes[i])
        
        ax.bar(timestamps[i], body_height, bottom=body_bottom, width=0.8/24, 
               color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    ax.set_title(f'{args.product} Candlestick Chart ({args.granularity})', fontsize=16)
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Price (USD)', fontsize=12)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.show()
else:
    print("Error: No candles data in response")
    print(json.dumps(parsed_response, indent=3))
