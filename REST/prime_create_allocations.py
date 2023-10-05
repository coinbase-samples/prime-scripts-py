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
import json, hmac, hashlib, time, uuid, os, base64, requests, argparse, sys
from urllib.parse import urlparse

# Must be entity or organization API key
API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
ORIGIN_PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

uri = 'https://api.prime.coinbase.com/v1/allocations'
timestamp = str(int(time.time()))
allocation_id = uuid.uuid4()
allocation_leg_id = uuid.uuid4()

product_id = 'ETH-USD'
size_type = 'PERCENT'

parser = argparse.ArgumentParser(description='Allocate funds to multiple portfolios')
parser.add_argument('--destination_portfolio_ids', '-d', nargs='+', required=True,
                    help='The UUIDs of the destination portfolios to which funds will be allocated')
parser.add_argument('--order_ids', '-o', nargs='+', required=True,
                    help='The UUIDs of the orders to be allocated to the destination portfolios')

args = parser.parse_args()

if not args.destination_portfolio_ids or not args.order_ids:
    sys.exit('Error: at least one value for both --destination_portfolio_ids and --order_ids is required')

# Calculate amount per destination_portfolio_id. Defaults to equal distribution
amount = 100 / len(args.destination_portfolio_ids)

allocation_legs = []
for dest_portfolio_id in args.destination_portfolio_ids:
    allocation_legs.append({
            'allocation_leg_id': allocation_leg_id,
            'destination_portfolio_id': dest_portfolio_id,
            'amount': str(amount)
        })

payload = {
    'allocation_id': str(allocation_id),
    'source_portfolio_id': ORIGIN_PORTFOLIO_ID,
    'product_id': product_id,
    'order_ids': args.order_ids,
    'allocation_legs': allocation_legs,
    'size_type': size_type
}

url_path = urlparse(uri).path
message = timestamp + 'POST' + url_path + json.dumps(payload)
signature_b64 = base64.b64encode(hmac.digest(SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
   'X-CB-ACCESS-SIGNATURE': signature_b64,
   'X-CB-ACCESS-timestamp': timestamp,
   'X-CB-ACCESS-KEY': API_KEY,
   'X-CB-ACCESS-PASSPHRASE': PASSPHRASE,
   'Accept': 'application/json'
}
response = requests.post(uri, json=payload, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
