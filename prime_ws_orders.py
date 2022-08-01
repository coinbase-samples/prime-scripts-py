"""
Copyright 2022 Coinbase Global, Inc.
 
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
http://www.apache.org/licenses/LICENSE-2.0
 
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json, hmac, hashlib, base64
import asyncio
import time
import websockets
import sys
import os
uri = 'wss://ws-feed.prime.coinbase.com'
ch = 'orders'
####CREDENTIALS AND SETTINGS
product_id = 'ETH-USD'
PASSPHRASE = os.environ.get("PASSPHRASE")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SIGNING_KEY = os.environ.get("SIGNING_KEY")
SVC_ACCOUNTID = os.environ.get("SVC_ACCOUNTID")
portfolio_id = os.environ.get("PORTFOLIO_ID")
s = time.gmtime(time.time())
TIMESTAMP = time.strftime('%Y-%m-%dT%H:%M:%SZ', s)
async def main_loop():
    async for websocket in websockets.connect(uri, ping_interval=None, max_size=None):
      try:
        signature = await sign(ch, ACCESS_KEY, SIGNING_KEY, SVC_ACCOUNTID, portfolio_id, product_id)
        print(signature)
        auth_message = json.dumps({
            'type': 'subscribe',
            'channel': ch,
            'access_key': ACCESS_KEY,
            'api_key_id': SVC_ACCOUNTID,
            'timestamp': TIMESTAMP,
            'passphrase': PASSPHRASE,
            'signature': signature,
            'portfolio_id': portfolio_id,
            'product_ids': [product_id]
        })
        await websocket.send(auth_message)
        processor = None
        while True:
          response = await websocket.recv()
          parsed = json.loads(response)
          print(json.dumps(parsed, indent=3))
      except websockets.ConnectionClosed:
          continue
async def sign(channel, key, secret, account_id, portfolio_id, product_ids):
    message = channel + key + account_id + TIMESTAMP + portfolio_id + product_ids
    print(message)
    signature = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
    signature_b64 = base64.b64encode(signature).decode()
    print(signature_b64)
    return signature_b64
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())