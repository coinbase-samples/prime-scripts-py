import json, hmac, hashlib, time, requests, base64, uuid
from urllib.parse import urlparse
import os

####credentials
api_key = os.environ.get("ACCESS_KEY")
secret_key = os.environ.get("SIGNING_KEY")
passphrase = os.environ.get("PASSPHRASE")
portfolio_id = os.environ.get("PORTFOLIO_ID")

####required variables
timestamp = str(int(time.time()))
client_order_id = uuid.uuid4()
method = 'GET'

#user inputs
product_id = 'ETH-USD'
#order_statuses = ''
#order_type = ''
#order_side = ''

url = 'https://api.prime.coinbase.com/v1/portfolios/'+portfolio_id+'/orders?product_ids='+product_id+'&sort_direction=DESC'

####signature and request
url_path = urlparse(url).path
message = timestamp + method + url_path
signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()
signature_b64 = base64.b64encode(signature).decode()

headers = {
   'X-CB-ACCESS-SIGNATURE': signature_b64,
   'X-CB-ACCESS-TIMESTAMP': timestamp,
   'X-CB-ACCESS-KEY': api_key,
   'X-CB-ACCESS-PASSPHRASE': passphrase,
   'Accept': 'application/json'
}
response = requests.get(url, headers=headers)
parse = json.loads(response.text)
print(json.dumps(parse, indent=3))