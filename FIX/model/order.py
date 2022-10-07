import quickfix as fix
import time
import uuid

class Order:

    def __init__(self, portfolio_id):
        self.portfolio_id = portfolio_id
        return

    def market_buy_base(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_BUY))
        message.setField(fix.Symbol("SOL-USD"))
        message.setField(fix.TimeInForce("3"))
        message.setField(fix.OrderQty(1))
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(847, "M")
        return message

    def market_buy_quote(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_BUY))
        message.setField(fix.Symbol("SOL-USD"))
        message.setField(fix.TimeInForce("3"))
        message.setField(fix.CashOrderQty(10))
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(847, "M")
        return message

    def market_sell_base(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.Symbol("SOL-USD"))
        message.setField(fix.TimeInForce("3"))
        message.setField(fix.OrderQty(1))
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(847, "M")
        return message

    def market_sell_quote(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.Symbol("SOL-USD"))
        message.setField(fix.TimeInForce("3"))
        message.setField(fix.CashOrderQty(10))
        message.setField(fix.OrdType(fix.OrdType_MARKET))
        message.setField(847, "M")
        return message


    def limit_buy_base(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_BUY))
        message.setField(fix.Symbol("DOGE-USD"))
        message.setField(fix.TimeInForce("1"))
        message.setField(fix.OrderQty(10))
        message.setField(fix.Price(2.00))
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
        message.setField(847, "L")
        return message

    def limit_sell_base(self):
        message = fix.Message()
        header = message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Account(self.portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.Symbol("SOL-USD"))
        message.setField(fix.TimeInForce("1"))
        message.setField(fix.OrderQty(1))
        message.setField(fix.Price(100.00))
        message.setField(fix.OrdType(fix.OrdType_LIMIT))
        message.setField(847, "L")
        return message

    def order_status_request(self, order_id, clord_id, symbol):
        order_status_message = fix.Message()
        header = order_status_message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_OrderStatusRequest))  # 35 = H
        order_status_message.setField(fix.OrderID(order_id))
        order_status_message.setField(fix.ClOrdID(clord_id))
        order_status_message.setField(fix.Symbol(symbol))
        return order_status_message

    def cancel_order(self, order):
        order_cancel_message = fix.Message()
        header = order_cancel_message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_OrderCancelRequest))  # 35 = F
        order_cancel_message.setField(fix.OrigClOrdID(order.getField(11)))
        order_cancel_message.setField(fix.Symbol("BTC-USD"))
        return order_cancel_message