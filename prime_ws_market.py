# Copyright 2022 Coinbase Global, Inc.
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
import asyncio, base64, hashlib, hmac, json, os, sys, time, websockets

PASSPHRASE = os.environ.get('PASSPHRASE')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
SVC_ACCOUNTID = os.environ.get('SVC_ACCOUNTID')

uri = 'wss://ws-feed.prime.coinbase.com'
timestamp = str(int(time.time()))
channel = 'l2_data'
product_id = 'ETC-USD'

async def main_loop():
  while True:
    try:
      async with websockets.connect(uri, ping_interval=None, max_size=None) as websocket:
        signature = sign(channel, ACCESS_KEY, SECRET_KEY, SVC_ACCOUNTID, product_id)
        auth_message = json.dumps({
            'type': 'subscribe',
            'channel': channel,
            'access_key': ACCESS_KEY,
            'api_key_id': SVC_ACCOUNTID,
            'timestamp': timestamp,
            'passphrase': PASSPHRASE,
            'signature': signature,
            'product_ids': [product_id]
        })
        await websocket.send(auth_message)
        while True:
          response = await websocket.recv()
          parsed_response = json.loads(response)
          print(json.dumps(parsed_response, indent=3))
    except websockets.ConnectionClosed:
      continue
    
def sign(channel, key, secret, account_id, product_ids):
    message = channel + key + account_id + timestamp + product_ids
    signature = hmac.digest(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    signature_b64 = base64.b64encode(signature).decode()
    return signature_b64

try:
    asyncio.get_event_loop().run_until_complete(main_loop())
except KeyboardInterrupt:
    print('\nClosing Prime websocket feed')
    sys.exit()
