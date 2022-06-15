import json, hmac, hashlib, time, base64, requests, uuid,os
from urllib.parse import urlparse

#prime credentials and portfolio ID
api_key = os.environ.get("ACCESS_KEY")
secret_key = os.environ.get("SIGNING_KEY")
passphrase = os.environ.get("PASSPHRASE")
portfolio_id = os.environ.get("PORTFOLIO_ID")

#method endpoint provided in Prime Docs
timestamp = str(int(time.time()))
method ='GET'
url = 'https://api.prime.coinbase.com/v1/portfolios/'+portfolio_id


#signature generation
url_path = urlparse(url).path
message = timestamp + method + url_path
signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
signature_b64 = base64.b64encode(signature).decode()
print('signature is: '+str(signature_b64))

headers = {
  'X-CB-ACCESS-SIGNATURE': signature_b64,
  'X-CB-ACCESS-TIMESTAMP': timestamp,
  'X-CB-ACCESS-KEY': api_key,
  'X-CB-ACCESS-PASSPHRASE': passphrase,
  'Accept': 'application/json'
}

response = requests.get(url, headers=headers)
parse = json.loads(response.text)
print('Status code: '+str(response.status_code))
print(json.dumps(parse, indent=3))