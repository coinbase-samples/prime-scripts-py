from logger import setup_logger
from setup import create_header
import logging
import quickfix as fix
from fix_session import Application

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


class Orders(Application):

    def get_order(self,fixSession):
        """Build Order Status Message (H) based-on user input"""

        message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderStatusRequest))
        message.setField(fix.OrderID(self.last_order_id))

        fixSession.send_message(message)
        logfix.info('Done: Retrieved Order Status!! \n')

    def cancel_order(self,fixSession):
        product = self.last_product_id[:7]
        client_order_id = self.last_client_order_id
        order_id = self.last_order_id
        side = self.last_side
        base_quantity = self.last_quantity[:-1]

        message = create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderCancelRequest))
        message.setField(fix.OrderID(str(order_id)))
        message.setField(fix.OrigClOrdID(str(client_order_id)))
        message.setField(fix.Symbol(str(product)))
        if side == '1':
            message.setField(fix.Side(fix.Side_BUY))
        else:
            message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.OrderQty(float(base_quantity)))
        fixSession.send_message(message)
        logfix.info('Done: submitted order cancellation!! \n')

