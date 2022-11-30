import logging
import time
from fix.order import collect_user_new_order_message, collect_user_get_order_status_message, collect_user_cancel_order_message, build_user_logout_message
from fix.logger import setup_logger

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
            collect_user_new_order_message(fixSession)
        if options == '2':
            collect_user_get_order_status_message(fixSession)
        if options == '3':
            collect_user_cancel_order_message(fixSession)
        if options == '4':
            build_user_logout_message(fixSession, sessionID)
        else:
            time.sleep(2)
