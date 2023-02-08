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

import configparser
# import certifi
import quickfix as fix
import logging
import time
from Model.logger import setup_logger, format_message
import base64
import hmac
import uuid
import json
import hashlib
import os
import sys

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

last_order_id = ''
last_client_order_id = ''
last_product_id = ''
last_side = ''
last_quantity = ''

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
            # logfix.info('Received Execution Report: ')
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


class Application(fix.Application):
    """FIX Application"""
    config = configparser.RawConfigParser()

    PASSPHRASE = str(os.environ.get('PASSPHRASE'))
    API_KEY = str(os.environ.get('API_KEY'))
    API_SECRET = str(os.environ.get('SECRET_KEY'))
    PORTFOLIO = str(os.environ.get('PORTFOLIO_ID'))

    def __init__(self):
        super().__init__()
        self.last_order_id = last_order_id
        self.last_client_order_id = last_client_order_id
        self.last_product_id = last_product_id
        self.last_side = last_side
        self.last_quantity = last_quantity
        self.firstRun = True


    def onCreate(self, sessionID):
        """Function called upon FIX Application startup"""
        logfix.info('onCreate : Session (%s)' % sessionID.toString())
        self.sessionID = sessionID
        self.fixSession = FixSession(self.sessionID, self.PORTFOLIO)
        return

    def onLogon(self, sessionID):
        """Function called upon Logon"""
        logfix.info('---------------Successful Logon----------------')
        self.sessionID = sessionID
        return

    def onLogout(self, sessionID):
        """Function called upon Logout"""
        #logfix.info('Session (%s) logout!' % sessionID.toString())
        return

    def toAdmin(self, message, sessionID):
        """Function called for all outbound Administrative Messages"""
        if message.getHeader().getField(35) == 'A':
            rawData = self.sign(message.getHeader().getField(52), message.getHeader().getField(35),
                                message.getHeader().getField(34), self.API_KEY, message.getHeader().getField(56),
                                self.PASSPHRASE)
            message.setField(fix.StringField(554, self.PASSPHRASE))
            message.setField(fix.StringField(96, rawData))
            message.setField(fix.StringField(9407, self.API_KEY))
            logfix.info('(Admin) S >> %s' % format_message(message))
            return
        else:
            return

    def fromAdmin(self, message, sessionID):
        """Function called for all inbound Administrative Messages"""
        if message.getHeader().getField(35) == 'A':
            logfix.info('(Admin) R << %s' % format_message(message))
        self.fixSession.on_message(message)
        return

    def toApp(self, message, sessionID):
        """Function called for outbound Application Messages"""
        logfix.info('(App) S >> %s' % format_message(message))
        self.last_client_order_id = message.getField(11)
        return

    def fromApp(self, message, sessionID):
        """Function called for inbound Application Messages"""
        logfix.info('(App) R << %s' % format_message(message))

        try:
            if message.getField(11) == self.last_client_order_id:
                self.last_order_id = message.getField(37)
                self.last_quantity = message.getField(151)
                self.last_side = message.getField(54)
                self.last_product_id = message.getField(55)

                order_details = {
                    'last_client_order_id': self.last_client_order_id,
                    'last_order_id': self.last_order_id,
                    'last_quantity': self.last_quantity,
                    'last_side': self.last_side,
                    'last_product_id': self.last_product_id
                }

                if self.firstRun:
                    order_json = json.dumps(order_details)
                    print(order_json)
                    self.firstRun = False

        except:
            print('no message')
        self.fixSession.on_message(message)
        return

    def sign(self, t, msg_type, seq_num, access_key, target_comp_id, passphrase):
        """Function to Generate Authentication Signature"""
        message = ''.join([t, msg_type, seq_num, access_key, target_comp_id, passphrase]).encode('utf-8')
        hmac_key = self.API_SECRET
        signature = hmac.new(hmac_key.encode('utf-8'), message, hashlib.sha256)
        sign_b64 = base64.b64encode(signature.digest()).decode()
        return sign_b64

    def build_create_order(self, fixSession, sessionID):
        """Construct FIX Message based on User Input"""
        time.sleep(1)
        self.create_order(fixSession)
        time.sleep(3)
        self.logout(fixSession, sessionID)

    def build_get_order(self, fixSession, sessionID):
        """Construct FIX Message based on User Input"""
        time.sleep(1)
        self.get_order(fixSession)
        time.sleep(3)
        self.logout(fixSession, sessionID)

    def build_cancel_order(self, fixSession, sessionID):
        """Construct FIX Message based on User Input"""
        time.sleep(1)
        self.cancel_order(fixSession)
        time.sleep(3)
        self.logout(fixSession, sessionID)

    def logout(self, fixSession, sessionID):
        """Build Cancel Order Message (F) based-on user input"""
        logout_message = fix.Message()
        header = logout_message.getHeader()
        header.setField(fix.MsgType(fix.MsgType_Logout))
        fixSession.send_message(logout_message)
        time.sleep(2)
        sys.exit()

    def run_create_order(self):
        """Run Application"""
        self.build_create_order(self.fixSession, self.sessionID)

    def run_get_order(self):
        """Run Application"""
        self.build_get_order(self.fixSession, self.sessionID)

    def run_cancel_order(self):
        """Run Application"""
        self.build_cancel_order(self.fixSession, self.sessionID)

