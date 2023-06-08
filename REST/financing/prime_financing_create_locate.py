# Copyright 2023-present Coinbase Global, Inc.
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
import sys, json, hmac, hashlib, time, os, base64, requests
from dateutil.relativedelta import relativedelta
from datetime import datetime

# must be an entity or organization API key
API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/locates'

timestamp = str(int(time.time()))
method = 'POST'

try:
    symbol = sys.argv[1].upper()
    amount = sys.argv[2]
except IndexError:
    print("Please provide symbol and amount separated by a space as command line arguments (e.g. ETH 1).")
    sys.exit(1)

time_offset = datetime.now() - relativedelta(days=3)
locate_time = time_offset.strftime('%Y-%m-%dT%H:%M:%SZ')

payload = {
    'symbol': symbol,
    'locate_time': locate_time,
    'amount': amount
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

response = requests.get(uri, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
