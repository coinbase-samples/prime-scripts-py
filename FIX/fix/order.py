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
from fix.logger import setup_logger
import quickfix as fix
import time, sys
import uuid
import datetime

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

def create_header(portfolio_id, message_type):
    """Build FIX Message Header"""
    message = fix.Message()
    header = message.getHeader()
    header.setField(message_type)
    message.setField(fix.Account(portfolio_id))
    message.setField(fix.ClOrdID(str(uuid.uuid4())))
    return message

def collect_user_new_order_message(fixSession):
    """Collect user input for NewOrderSingle(D)"""
    product = str(input('Please enter a product such as ETH-USD: '))
    order_type = str(input('Please choose one of the following order types: \n'
                           '1: Market Order\n'
                           '2: Limit Order\n'
                           '3: TWAP Order\n'))

    if (order_type == '2') or (order_type == '3'):
        limit_price = str(input('Please enter a limit price such as 100: '))
    else:
        limit_price = None
    if order_type == '3':
        expire_time = str(input('Please enter an expiration time such as 20230123-03:52:24.824: '))
    else:
        expire_time = None
    side = str(input('Please choose one of the following sides: \n'
                     '1: BUY\n'
                     '2: SELL\n'))
    base_or_quote = str(input('Please specify if this order is in base or quote: \n'
                              '1: BASE Order\n'
                              '2: QUOTE Order\n'))
    if base_or_quote == '1':
        base_quantity = str(input("Enter quantity such as 0.25: "))
        cash_order_quantity = None
    elif base_or_quote == '2':
        cash_order_quantity = str(input("Enter cash quantity such as 10.00: "))
        base_quantity = None

    order = {
        "product": product,
        "order_type": order_type,
        "order_side": side,
        "order_base_quote": base_or_quote,
        "base_quantity": base_quantity,
        "cash_order_quantity": cash_order_quantity,
        "limit_price": limit_price,
        "expire_time": expire_time
    }
    build_create_new_order_message(order, fixSession)

def build_create_new_order_message(order, fixSession):
    """Build NewOrderSingle (D) based-on user input"""
    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_NewOrderSingle))
    message.setField(fix.Symbol(order.get("product")))

    if order.get("order_type") == '1':
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(fix.TimeInForce('3'))
        message.setField(847, 'M')
    elif order.get("order_type") == '2':
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
        message.setField(fix.TimeInForce('1'))
        message.setField(847, 'L')
        message.setField(fix.Price(float(order.get("limit_price"))))
    else:
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
        expire_time = fix.ExpireTime()
        expire_time.setString(order.get("expire_time"))
        message.setField(expire_time)
        effective_time = fix.EffectiveTime()
        effective_time.setString(datetime.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"));
        message.setField(effective_time)
        message.setField(fix.TimeInForce("6"))
        message.setField(fix.Price(float(order.get("limit_price"))))
        message.setField(847, "T")
    if order.get("order_side") == '1':
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

def collect_user_get_order_status_message(fixSession):
    """Collect user input for OrderStatusMessage(H)"""
    order_id = str(input('Please enter an order_id such as \'a51f2695-9c6d-4330-bfce-09c6a8ce9c64\': '))
    logfix.info("Getting Order Status...")
    build_get_order_status_message(order_id, fixSession)

def build_get_order_status_message(order_id, fixSession):
    """Build Order Status Message (H) based-on user input"""
    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderStatusRequest))
    message.setField(fix.OrderID(order_id))

    #logfix.info("Getting Order Status...")
    fixSession.send_message(message)
    logfix.info('Done: Retrieved Order Status \n')

def collect_user_cancel_order_message(fixSession):
    """Collect User Input for Order Cancel Request (F)"""
    product = 'ETH-USD'
    orig_clor_id = str(
        input(
            'Please enter the Client Order ID from the original order such as a51f2695-9c6d-4330-bfce-09c6a8ce9c64: '))
    order_id = str(
        input('Please enter the Order ID from the original order such as a51f2695-9c6d-4330-bfce-09c6a8ce9c64: '))
    side = str(input('Please choose one of the following sides: \n'
                     '1: BUY\n'
                     '2: SELL\n'))
    base_or_quote = str(input('Please specify if this order is in base or quote: \n'
                              '1: BASE Order\n'
                              '2: QUOTE Order\n'))
    if base_or_quote == '1':
        base_quantity = str(input("Enter quantity such as 0.25: "))
        cash_order_quantity = None
    elif base_or_quote == '2':
        cash_order_quantity = str(input("Enter cash quantity such as 10.00: "))
        base_quantity = None

    order = {
        "product": product,
        "orig_clor_id": orig_clor_id,
        "order_id": order_id,
        "order_side": side,
        "order_base_quote": base_or_quote,
        "base_quantity": base_quantity,
        "cash_order_quantity": cash_order_quantity,
    }
    logfix.info("Cancelling Order...")
    build_cancel_order_message(order, fixSession)

def build_cancel_order_message(order, fixSession):
    """Build Cancel Order Message (F) based-on user input"""
    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderCancelRequest))
    message.setField(fix.Symbol(order.get("product")))
    message.setField(fix.OrderID(str(order.get("order_id"))))
    message.setField(fix.OrigClOrdID(str(order.get("orig_clor_id"))))
    message.setField(fix.Symbol(str(order.get("product"))))
    if order.get("order_side") == '1':
        message.setField(fix.Side(fix.Side_BUY))
    else:
        message.setField(fix.Side(fix.Side_SELL))
    if order.get("base_quantity"):
        message.setField(fix.OrderQty(float(order.get("base_quantity"))))
    else:
        message.setField(fix.CashOrderQty(float(order.get("cash_order_quantity"))))
    fixSession.send_message(message)

def build_user_logout_message(fixSession, sessionID):
    """Build Cancel Order Message (F) based-on user input"""
    logout_message = fix.Message()
    header = logout_message.getHeader()
    header.setField(fix.MsgType(fix.MsgType_Logout))
    fixSession.send_message(logout_message)
    time.sleep(2)
    sys.exit()