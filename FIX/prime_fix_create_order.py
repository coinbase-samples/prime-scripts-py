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
import logging
import quickfix as fix
from logger import setup_logger
from setup import create_header

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


def build_create_new_order_message(fixSession):
    """Build NewOrderSingle (D) based-on user input"""

    product = 'ETH-USD'
    order_type = 'LIMIT'  # market, limit, or TWAP
    side = 'BUY'  # BUY or SELL
    base_quantity = '0.0015'
    limit_price = '1001'  # None or e.g. '1000'
    expire_time = None  # None or e.g. '20230123-03:52:24.824'

    order = {
        "product": product,
        "order_type": order_type,
        "order_side": side,
        "base_quantity": base_quantity,
        "limit_price": limit_price,
        "expire_time": expire_time
    }

    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_NewOrderSingle))
    message.setField(fix.Symbol(order.get("product")))

    if order.get("order_type") == 'MARKET':
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(fix.TimeInForce('3'))
        message.setField(847, 'M')
    elif order.get("order_type") == 'LIMIT':
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
        message.setField(fix.TimeInForce('1'))
        message.setField(847, 'L')
        message.setField(fix.Price(float(order.get("limit_price"))))
    if order.get("order_side") == 'BUY':
        message.setField(fix.Side(fix.Side_BUY))
    else:
        message.setField(fix.Side(fix.Side_SELL))
    if order.get("base_quantity"):
        message.setField(fix.OrderQty(float(order.get("base_quantity"))))
    else:
        message.setField(fix.CashOrderQty(float(order.get("cash_order_quantity"))))

    logfix.info("Submitting Order...")
    fixSession.send_message(message)
    logfix.info('Done: Put New Order\n')
    response = str(message)
    orig_client_order_id = response.split('11=', 1)[1][:36]
    print('clorid: ' + str(orig_client_order_id))
    return orig_client_order_id

