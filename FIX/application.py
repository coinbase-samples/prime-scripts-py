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
import quickfix as fix
import logging
from message import build_message
from logger import setup_logger, format_message
import base64
import hmac
import hashlib
from fix_session import FixSession
import os
from dotenv import load_dotenv
from prime_fix_get_order import get_order_status_message

load_dotenv()

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')


class Application(fix.Application):
    """FIX Application"""
    config = configparser.RawConfigParser()

    PASSPHRASE = str(os.environ.get('PASSPHRASE'))
    API_KEY = str(os.environ.get('API_KEY'))
    API_SECRET = str(os.environ.get('SECRET_KEY'))
    PORTFOLIO = str(os.environ.get('PORTFOLIO_ID'))

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
        logfix.info('Session (%s) logout!' % sessionID.toString())
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

        return

    def fromApp(self, message, sessionID):
        """Function called for inbound Application Messages"""
        logfix.info('(App) R << %s' % format_message(message))
        response = str(message)

        try:
            #client_order_id = response.split('11=', 1)[1][:36]
            #if client_order_id == orig_client_order_id:
            #     order_id = response.split('37=', 1)[1][:36]
            #     print('order_id: ' + str(order_id))
            order_id = response.split('37=', 1)[1][:36]
            print(order_id)
            #self.orderID = order_id
            #get_order_status_message(self.fixSession, order_id)
        except:
            print('no message')
        self.fixSession.on_message(message)
        return order_id

    def sign(self, t, msg_type, seq_num, access_key, target_comp_id, passphrase):
        """Function to Generate Authentication Signature"""
        message = ''.join([t, msg_type, seq_num, access_key, target_comp_id, passphrase]).encode('utf-8')
        hmac_key = self.API_SECRET
        signature = hmac.new(hmac_key.encode('utf-8'), message, hashlib.sha256)
        sign_b64 = base64.b64encode(signature.digest()).decode()
        return sign_b64

    def run(self):
        """Run Application"""
        build_message(self.fixSession, self.sessionID)

