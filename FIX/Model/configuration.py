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
import os
import certifi
import configparser
import quickfix as fix
import uuid


def create_header(portfolio_id, message_type):
    message = fix.Message()
    header = message.getHeader()
    header.setField(message_type)
    message.setField(fix.Account(portfolio_id))
    message.setField(fix.ClOrdID(str(uuid.uuid4())))
    return message


class Configuration:
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

        with open('../example.cfg', 'w') as configfile:
            self.config.write(configfile)