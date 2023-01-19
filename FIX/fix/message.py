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
import time
from fix.logger import setup_logger
from fix.create_order import build_create_new_order_message
from fix.get_order import get_order_status_message
from fix.cancel_order import build_order_cancel
from fix.setup import build_user_logout_message

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

def build_message(fixSession, sessionID):
    """Construct FIX Message based on User Input"""

    while True:
        time.sleep(1)
        options = str(input('Please choose one of the following: \n'
                            '1: Place New Order\n'
                            '2: Get Order Status\n'
                            '3: Cancel Order\n'
                            '4: Exit Application!\n'))
        if options == '1':
            #collect_user_new_order_message(fixSession)
            build_create_new_order_message(fixSession)
        if options == '2':
            #collect_user_get_order_status_message(fixSession)
            get_order_status_message(fixSession)
        if options == '3':
            #collect_user_cancel_order_message(fixSession)
            build_order_cancel(fixSession)
        if options == '4':
            build_user_logout_message(fixSession, sessionID)
        else:
            time.sleep(2)
