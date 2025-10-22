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

import asyncio
import base64
import hashlib
import hmac
import json
import os
import sys
import time

import websockets

PASSPHRASE = os.environ.get('PASSPHRASE')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
SVC_ACCOUNTID = os.environ.get('SVC_ACCOUNTID')

uri = 'wss://ws-feed.prime.coinbase.com'
product_ids = ['BTC-USD']


def sign(channel: str, key: str, account_id: str, product_ids: list, timestamp: str) -> str:
    message = channel + key + account_id + timestamp + "".join(product_ids)
    signature = hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode()


async def main_loop():
    try:
        async with websockets.connect(uri, ping_interval=None, max_size=None) as websocket:
            for ch in ['l2_data', 'heartbeats']:
                timestamp = str(int(time.time()))
                signature = sign(ch, ACCESS_KEY, SVC_ACCOUNTID, product_ids, timestamp)
                auth_message = json.dumps({
                    'type': 'subscribe',
                    'channel': ch,
                    'access_key': ACCESS_KEY,
                    'api_key_id': SVC_ACCOUNTID,
                    'timestamp': timestamp,
                    'passphrase': PASSPHRASE,
                    'signature': signature,
                    'product_ids': product_ids
                })
                await websocket.send(auth_message)

            while True:
                response = await websocket.recv()
                parsed_response = json.loads(response)

                if parsed_response.get("type") == "snapshot":
                    continue

                print(json.dumps(parsed_response, indent=3))
    except websockets.ConnectionClosed:
        print("Connection closed, exiting...")
    except KeyboardInterrupt:
        print("\nInterrupted, exiting...")
        sys.exit()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_loop())
