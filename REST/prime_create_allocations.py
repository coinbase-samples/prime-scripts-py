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
import json, hmac, hashlib, time, uuid, os, base64, requests

ORG_API_KEY = os.environ.get('ORG_ACCESS_KEY')
ORG_SECRET_KEY = os.environ.get('ORG_SIGNING_KEY')
ORG_PASSPHRASE = os.environ.get('ORG_PASSPHRASE')
ORIGIN_PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

uri = f'https://api.prime.coinbase.com/v1/allocations'
timestamp = str(int(time.time()))
method = 'POST'
allocation_id = uuid.uuid4()

product_id = 'ETH-USD'
destination_portfolio_id = 'destination_portfolio_id'
amount = '0.02'
size_type = 'BASE'

order_ids = [
    'order_id_1',
    'order_id_2'
]

allocation_legs = [{
            'allocation_leg_id': ORIGIN_PORTFOLIO_ID,
            'destination_portfolio_id': destination_portfolio_id,
            'amount': amount
        }]

payload = {
    'allocation_id': str(allocation_id),
    'source_portfolio_id': ORIGIN_PORTFOLIO_ID,
    'product_id': product_id,
    'order_ids': order_ids,
    'allocation_legs': allocation_legs,
    'size_type': size_type
}

url_path = urlparse(uri).path
message = timestamp + method + url_path + json.dumps(payload)
signature_b64 = base64.b64encode(hmac.digest(ORG_SECRET_KEY.encode(), message.encode(), hashlib.sha256))

headers = {
   'X-CB-ACCESS-SIGNATURE': signature_b64,
   'X-CB-ACCESS-timestamp': timestamp,
   'X-CB-ACCESS-KEY': ORG_API_KEY,
   'X-CB-ACCESS-PASSPHRASE': ORG_PASSPHRASE,
   'Accept': 'application/json'
}
response = requests.post(uri, json=payload, headers=headers)
parsed_response = json.loads(response.text)
print(json.dumps(parsed_response, indent=3))
