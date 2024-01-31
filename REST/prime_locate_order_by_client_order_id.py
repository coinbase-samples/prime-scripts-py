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


def list_orders(uri):
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
    if response.status_code != 200:
        print(f'Failed to list orders: HTTP {response.status_code} - {response.text}')
        return None
    return json.loads(response.text)


def search_order(client_order_id, parsed_response):
    for order in parsed_response.get('orders', []):
        if order.get('client_order_id') == client_order_id:
            return order
    return None


base_uri = f'https://api.prime.coinbase.com/v1/portfolios/{PORTFOLIO_ID}/orders'
uri = base_uri

order_found = None

while True:
    parsed_response = list_orders(uri)
    if not parsed_response:
        break

    order_found = search_order(client_order_id_to_check, parsed_response)
    if order_found:
        break

    pagination_info = parsed_response.get('pagination', {})

    if pagination_info.get('has_next'):
        next_cursor = pagination_info.get('next_cursor')
        uri = f'{base_uri}?cursor={next_cursor}'
    else:
        break

if order_found:
    print(f'Order found:\n  Client Order ID: {client_order_id_to_check}\n  Associated Order ID: {order_found.get("id")}')
else:
    print(f'Order with client_order_id {client_order_id_to_check} not found.')
