import logging
import quickfix as fix
import uuid
from model.logger import setup_logger
import time
from model.order import Order

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

class FixSession:

    def __init__(self, session_id, portfolio_id):
        self.session_id = session_id
        self.open_order_client_oid = ''
        self.order = Order(portfolio_id)

    def place_order(self):
        """Request sample new order single"""
        message = self.order.market_buy_base()
        fix.Session.sendToTarget(message, self.session_id)
        return message

    def place_open_limit_order(self):
        """Test Order Functionality placing a limit order that does not fill"""
        message = self.order.limit_buy_base()
        fix.Session.sendToTarget(message, self.session_id)
        return message

    def onMessage(self, message):
        """Processing application message here"""
        logfix.info("--------------onMessage()--------------")
        self.order_id = message.getField(37)
        self.clord_id = message.getField(11)
        self.symbol = message.getField(55)
        if message.getHeader().getField(35) == "8":
            logfix.info("Received Execution Report: ")
            if (message.getField(150) == "0"):
                logfix.info("New Order - Order Not Filled")
            elif (message.getField(150) == "1"):
                logfix.info("Order - Partial fill")
            elif (message.getField(150) == "2"):
                logfix.info("Order - Filled")
            elif message.getField(150) == "3":
                logfix.info("Order {} Done".format(self.order_id))
            elif message.getField(150) == "4":
                logfix.info("Order {} Cancelled".format(self.order_id))
            elif message.getField(150) == "7":
                logfix.info("Order {} Stopped".format(self.order_id))
            elif message.getField(150) == "8":
                logfix.info("Order {} Rejected".format(self.order_id))
            elif message.getField(150) == "D":
                logfix.info("Order {} Restated".format(self.order_id))
            elif message.getField(150) == "I":
                logfix.info("Order Status for {} : {}".format(self.order_id, message))
            else:
                return

    def get_order_status(self):
        '''Send Order Status Request Message (H)'''
        order_status_message = self.order.order_status_request(self.order_id, self.clord_id, self.symbol)
        fix.Session.sendToTarget(order_status_message, self.session_id)
        return order_status_message