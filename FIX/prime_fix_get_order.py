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
# from application import Application
# application = Application()


setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


def get_order_status_message(fixSession,order_id):
    """Build Order Status Message (H) based-on user input"""

    # order_id = '3e4062e3-0813-4662-9825-9ad3e1879ee6'

    message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderStatusRequest))
    message.setField(fix.OrderID(order_id))

    fixSession.send_message(message)
    logfix.info('Done: Retrieved Order Status \n')
