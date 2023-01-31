from logger import setup_logger
import logging
import quickfix as fix
from fix_session import Application

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


class Orders(Application):

    def create_order(self, fixSession):
        """Build NewOrderSingle (D) based-on user input"""

        product = 'ETH-USD'
        order_type = 'LIMIT'  # market, limit, or TWAP
        side = 'BUY'
        base_quantity = '0.0015'
        limit_price = '1001'

        message = self.create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Symbol(product))

        if order_type == 'MARKET':
            message.setField(fix.OrdType(fix.OrdType_MARKET))
            message.setField(fix.TimeInForce('3'))
            message.setField(847, 'M')
        elif order_type == 'LIMIT':
            message.setField(fix.OrdType(fix.OrdType_LIMIT))
            message.setField(fix.TimeInForce('1'))
            message.setField(847, 'L')
            message.setField(fix.Price(float(limit_price)))
        if side == 'BUY':
            message.setField(fix.Side(fix.Side_BUY))
        else:
            message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.OrderQty(float(base_quantity)))

        logfix.info("Submitting Order...")
        fixSession.send_message(message)
        logfix.info('Done: Put New Order\n')


    def get_order(self,fixSession):
        """Build Order Status Message (H) based-on user input"""
        last_order_id = self.q.get()

        message = self.create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderStatusRequest))
        message.setField(fix.OrderID(last_order_id))

        fixSession.send_message(message)
        logfix.info('Done: Retrieved Order Status!! \n')

    def cancel_order(self,fixSession):

        order_id = self.q.get(self.last_order_id)
        client_order_id = self.q.get(self.last_client_order_id)
        base_quantity = self.q.get(self.last_quantity)
        side = self.q.get(self.last_side)
        product = self.q.get(self.last_product_id)

        message = self.create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_OrderCancelRequest))
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

