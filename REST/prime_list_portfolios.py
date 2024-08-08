# Copyright 2022-present Coinbase Global, Inc.
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
import json, hmac, hashlib, time, os, base64, requests

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')

uri = 'https://api.prime.coinbase.com/v1/portfolios'
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
