#!/usr/bin/python
# -*- coding: utf8 -*-
"""FIX Application"""
import configparser
import quickfix as fix
import logging
from fix.message import build_message
from fix.logger import setup_logger, format_message
import base64
import hmac
import hashlib
from fix_session import FixSession

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

class Application(fix.Application):
    """FIX Application"""
    config = configparser.RawConfigParser()
    config.read('./fix/resources/prime.properties')

    PASSPHRASE = str(config.get('session_1', 'passphrase'))
    API_KEY = str(config.get('session_1', 'api_key'))
    API_SECRET = str(config.get('session_1', 'api_secret'))
    PORTFOLIO = str(config.get('session_1', 'portfolio'))

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
        logfix.info('Session (%s) logout !' % sessionID.toString())
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
        self.fixSession.on_message(message)
        return

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