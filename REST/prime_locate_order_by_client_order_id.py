from urllib.parse import urlparse
import json, hmac, hashlib, time, os, base64, requests, sys

if len(sys.argv) < 2:
    print('Usage: python prime_locate_order_by_client_order_id.py <client_order_id>')
    sys.exit(1)

client_order_id_to_check = sys.argv[1]

API_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SIGNING_KEY')
PASSPHRASE = os.environ.get('PASSPHRASE')
PORTFOLIO_ID = os.environ.get('PORTFOLIO_ID')

uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/orders'
url_path = urlparse(uri).path
timestamp = str(int(time.time()))
message = timestamp + 'GET' + url_path
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

# Search for the order with the specified client_order_id
order_found = False
for order in parsed_response.get('orders', []):
    if order.get('client_order_id') == client_order_id_to_check:
        order_id = order.get('id')
        print(f'Order found:\n  Client Order ID: {client_order_id_to_check}\n  Associated Order ID: {order_id}')
        order_found = True
        break

if not order_found:
    print(f'Order with client_order_id {client_order_id_to_check} not found.')