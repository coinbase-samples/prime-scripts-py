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

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


class FixSession:
    """FIX Session"""

    def __init__(self, session_id, portfolio_id):
        self.session_id = session_id
        self.portfolio_id = portfolio_id

    def send_message(self, message):
        """Sending FIX Messages to API here"""
        fix.Session.sendToTarget(message, self.session_id)

    def on_message(self, message):
        """Process Application messages here"""
        if message.getHeader().getField(35) == '8' and '20=0' in str(message):
            logfix.info('Received Execution Report: ')
            self.get_exec_type(message)
        elif message.getHeader().getField(35) == '3':
            if "58=" in str(message):
                reason = message.getField(58)
                logfix.info('Message Rejected, Reason: {} '.format(reason))
            else:
                reason = 'Not Returned'
                logfix.info('Message Rejected, Reason: {} '.format(reason))

    def get_exec_type(self, message):
        """Util Function to parse Execution Reports"""
        exec_type = message.getField(150)
        if "58=" in str(message):
            reason = message.getField(58)
        else:
            reason = 'Not Returned'
        order_id = message.getField(37)
        symbol = message.getField(55)

        if exec_type == '0':
            logfix.info('New Order - Order Not Filled')
        elif exec_type == '1':
            logfix.info('Order - Partial fill')
        elif exec_type == '2':
            logfix.info('Order - Filled')
        elif exec_type == '3':
            logfix.info('Order {} Done'.format(order_id))
        elif exec_type == '4':
            logfix.info('Order {} Cancelled, Reason: {}'.format(order_id, reason))
        elif exec_type == '7':
            logfix.info('Order {} Stopped, Reason: {}'.format(order_id, reason))
        elif exec_type == '8':
            logfix.info('Order {} Rejected, Reason: {}'.format(order_id, reason))
        elif exec_type == 'D':
            logfix.info('Order {} Restated, Reason: {}'.format(order_id, reason))
        elif exec_type == 'I':
            logfix.info('Order Status for {} : {}'.format(order_id, message))
        else:
            return
