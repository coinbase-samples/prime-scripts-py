import configparser
import certifi

properties = configparser.RawConfigParser()
properties.read('./fix/resources/prime.properties')

class Configuration:
    """FIX Configuration"""
    BEGIN_STRING = str(properties.get('session_1', 'fix_version'))
    SENDER_COMP_ID = str(properties.get('session_1', 'sender_comp_id'))
    TARGET_COMP_ID = str(properties.get('session_1', 'target_comp_id'))
    CLIENT_CERTIFICATE_KEY_FILE = str(certifi.where())

    def __init__(self):
        self.config = configparser.ConfigParser()

    def build_config(self):
        """Function to build example.cfg file for FIX Client"""
        self.config['DEFAULT'] = {
            'ConnectionType': 'initiator',
            'FileLogPath' : './Logs/',
            'StartTime' :'00:00:00',
            'EndTime' : '00:00:00',
            'UseDataDictionary' :'N',
            'ReconnectInterval':'10',
            'ValidateUserDefinedFields':'N',
            'ValidateIncomingMessage':'Y',
            'ResetOnLogon':'Y',
            'ResetOnLogout':'N',
            'ResetOnDisconnect':'Y',
            'ClientCertificateKeyFile': self.CLIENT_CERTIFICATE_KEY_FILE,
            'SSLEnable':'Y',
            'SSLProtocols':'Tls12',
            'SocketConnectPort':'4198'
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

