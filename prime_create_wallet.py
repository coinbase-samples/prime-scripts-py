import json, hmac, hashlib, time, requests, base64, uuid, os
from urllib.parse import urlparse

####credentials
api_key = os.environ.get("ACCESS_KEY")
secret_key = os.environ.get("SIGNING_KEY")
passphrase = os.environ.get("PASSPHRASE")
portfolio_id = os.environ.get("PORTFOLIO_ID")

####required variables
timestamp = str(int(time.time()))
idempotency_key = uuid.uuid4()
method = "POST"

#user inputs
wallet_name = os.environ.get("WALLET_NAME")

url = "https://api.prime.coinbase.com/v1/portfolios/"+portfolio_id+"/wallets"
payload = {
    "portfolio_id": portfolio_id,
    "name": wallet_name,
    "symbol": "eth",
    "wallet_type": "VAULT"
    }

####signature and request
url_path = urlparse(url).path
message = timestamp + method + url_path + json.dumps(payload)
signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
signature_b64 = base64.b64encode(signature).decode()

headers = {
   'X-CB-ACCESS-SIGNATURE': signature_b64,
   'X-CB-ACCESS-TIMESTAMP': timestamp,
   'X-CB-ACCESS-KEY': api_key,
   'X-CB-ACCESS-PASSPHRASE': passphrase,
   'Accept': 'application/json'
}
response = requests.post(url, json=payload, headers=headers)
parse = json.loads(response.text)
print(response.status_code)
print(json.dumps(parse, indent=3))