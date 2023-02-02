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
import certifi
import quickfix as fix
import logging
import time
from logger import setup_logger, format_message
import base64
import hmac
import uuid
import hashlib
import os
import sys
import queue
from dotenv import load_dotenv

load_dotenv()

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


class Configuration:
    """FIX Configuration"""
    BEGIN_STRING = str(os.environ.get('FIX_VERSION'))
    SENDER_COMP_ID = str(os.environ.get('SVC_ACCOUNT_ID'))
    TARGET_COMP_ID = str(os.environ.get('TARGET_COMP_ID'))
    CLIENT_CERTIFICATE_KEY_FILE = str(certifi.where())

    def __init__(self):
        self.config = configparser.ConfigParser()

    def build_config(self):
        """Function to build example.cfg file for FIX Client"""
        self.config['DEFAULT'] = {
            'ConnectionType': 'initiator',
            'FileLogPath': './Logs/',
            'StartTime': '00:00:00',
            'EndTime': '00:00:00',
            'UseDataDictionary': 'N',
            'ReconnectInterval': '10',
            'ValidateUserDefinedFields': 'N',
            'ValidateIncomingMessage': 'Y',
            'ResetOnLogon': 'Y',
            'ResetOnLogout': 'N',
            'ResetOnDisconnect': 'Y',
            'ClientCertificateKeyFile': self.CLIENT_CERTIFICATE_KEY_FILE,
            'SSLEnable': 'Y',
            'SSLProtocols': 'Tls12',
            'SocketConnectPort': '4198'
        }

        self.config['SESSION'] = {
            'BeginString': self.BEGIN_STRING,
            'SenderCompID': self.SENDER_COMP_ID,
            'TargetCompID': self.TARGET_COMP_ID,
            'HeartBtInt': '30',
            'SocketConnectHost': 'fix.prime.coinbase.com',
            'FileStorePath': './Sessions/'
        }

        with open('example.cfg', 'w') as configfile:
            self.config.write(configfile)


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
        self.q = queue.Queue()

    def create_header(self, portfolio_id, message_type):
        """Build FIX Message Header"""
        message = fix.Message()
        header = message.getHeader()
        header.setField(message_type)
        message.setField(fix.Account(portfolio_id))
        message.setField(fix.ClOrdID(str(uuid.uuid4())))
        return message

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
            client_order_id = response.split('11=', 1)[1][:36]
            order_id = response.split('37=', 1)[1][:36]
            quantity = response[response.find('151=') + 4:response.find('10=')]
            quantity = bytes(quantity, 'utf-8').decode('utf-8', 'ignore')
            side = response.split('54=', 1)[1][:1]
            if '60=' in response:
                product_id = response[response.find('55=') + 3:response.find('60=')]
            else:
                product_id = response[response.find('55=') + 3:response.find('78=')]
            self.last_order_id = order_id
            self.last_client_order_id = client_order_id
            self.last_quantity = quantity.translate(dict.fromkeys(range(32)))
            self.last_side = side
            self.last_product_id = product_id.translate(dict.fromkeys(range(32)))
            if self.q.empty():
                self.q.put(self.last_order_id)
                self.q.put(self.last_order_id)
                self.q.put(self.last_client_order_id)
                self.q.put(self.last_quantity)
                self.q.put(self.last_side)
                self.q.put(self.last_product_id)

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

    def build_message(self, fixSession, sessionID):
        """Construct FIX Message based on User Input"""
        time.sleep(1)
        self.create_order(fixSession)
        time.sleep(1)
        self.get_order(fixSession)
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

    def run(self):
        """Run Application"""
        self.build_message(self.fixSession, self.sessionID)

