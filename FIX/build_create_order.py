# Copyright 2023-present Coinbase Global, Inc.
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
import quickfix as fix
from app.fix_session import Application
from app.dictionary import type_market, type_limit, side_buy


class BuildCreate(Application):

    def create_order(self, fixSession):

        product = 'ETH-USD'
        order_type = 'LIMIT'
        side = 'BUY'
        base_quantity = '0.0015'
        limit_price = '1001'

        message = self.create_header(fixSession.portfolio_id, fix.MsgType(fix.MsgType_NewOrderSingle))
        message.setField(fix.Symbol(product))

        if order_type == type_market:
            message.setField(fix.OrdType(fix.OrdType_MARKET))
            message.setField(fix.TimeInForce('3'))
            message.setField(847, 'M')
        elif order_type == type_limit:
            message.setField(fix.OrdType(fix.OrdType_LIMIT))
            message.setField(fix.TimeInForce('1'))
            message.setField(847, 'L')
            message.setField(fix.Price(float(limit_price)))
        if side == side_buy:
            message.setField(fix.Side(fix.Side_BUY))
        else:
            message.setField(fix.Side(fix.Side_SELL))
        message.setField(fix.OrderQty(float(base_quantity)))

        fixSession.send_message(message)
