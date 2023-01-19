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
from fix.logger import setup_logger
from fix.setup import create_header

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

def build_order_cancel(fixSession):

    # order type
    product = 'ETH-USD'
    client_order_id = 'a42da462-4aa0-4b2f-adb4-ba507b025350'
    order_id = '3e4062e3-0813-4662-9825-9ad3e1879ee6'
    side = 'BUY'
    base_quantity = '0.0015'

    order = {
        "product": product,
        "client_order_id": client_order_id,
        "order_id": order_id,
        "order_side": side,
        "base_quantity": base_quantity
    }

    print(order)

    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderCancelRequest))
    message.setField(fix.Symbol(order.get("product")))
    message.setField(fix.OrderID(order.get("order_id")))
    message.setField(fix.OrigClOrdID(order.get("client_order_id")))
    if order.get("order_side") == 'BUY':
        message.setField(fix.Side(fix.Side_BUY))
    else:
        message.setField(fix.Side(fix.Side_SELL))
    message.setField(fix.OrderQty(float(order.get("base_quantity"))))
    fixSession.send_message(message)