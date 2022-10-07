#!/usr/bin/python
# -*- coding: utf8 -*-
"""FIX Application"""
import configparser
import sys
import quickfix as fix
import logging
from model.logger import setup_logger
import time
import base64
import hmac
import hashlib
import os

__SOH__ = "\u0001"

from fix_session import FixSession

setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

class Application(fix.Application):
    """FIX Application"""
    fix_sessions = []

    PASSPHRASE = os.environ.get('PASSPHRASE')
    API_KEY = os.environ.get('ACCESS_KEY')
    API_SECRET = os.environ.get('SIGNING_KEY')
    PORTFOLIO = os.environ.get('PORTFOLIO_ID')

    def onCreate(self, sessionID):
        logfix.info("onCreate : Session (%s)" % sessionID.toString())
        self.sessionID = sessionID
        self.fixSession = FixSession(self.sessionID, self.PORTFOLIO)
        self.fix_sessions.append(self.fixSession)
        return

    def onLogon(self, sessionID):
        logfix.info("---------------Successful Logon----------------")
        self.sessionID = sessionID
        return

    def onLogout(self, sessionID):
        logfix.info("Session (%s) logout !" % sessionID.toString())
        return

    def toAdmin(self, message, sessionID):
        if message.getHeader().getField(35) == "A":
            rawData = self.sign(message.getHeader().getField(52), message.getHeader().getField(35),
                                message.getHeader().getField(34), self.API_KEY, message.getHeader().getField(56),
                                self.PASSPHRASE)
            message.setField(fix.StringField(554, self.PASSPHRASE))
            message.setField(fix.StringField(96, rawData))
            message.setField(fix.StringField(9407, self.API_KEY))
            msg = message.toString().replace(__SOH__, "|")
            logfix.info("(Admin) S >> %s" % msg)
            return
        else:
            return

    def fromAdmin(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(Admin) R << %s" % msg)
        return

    def toApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) S >> %s" % msg)
        return

    def fromApp(self, message, sessionID):
        msg = message.toString().replace(__SOH__, "|")
        logfix.info("(App) R << %s" % msg)
        self.fixSession.onMessage(message)
        return

    def sign(self, t, msg_type, seq_num, access_key, target_comp_id, passphrase):
        message = ''.join([t, msg_type, seq_num, access_key, target_comp_id, passphrase]).encode("utf-8")
        hmac_key = self.API_SECRET
        signature = hmac.new(hmac_key.encode('utf-8'), message, hashlib.sha256)
        sign_b64 = base64.b64encode(signature.digest()).decode()
        return sign_b64

    def run(self):
        """Run"""
        while 1:
            options = str(input("Please choose one of the following: \n"
                                "1: Place New Order\n"
                                "2: Get Order Status\n"
                                "3: Cancel Order\n"
                                "4: Exit Application!\n"))
            if options == '1':
                msg = self.fixSession.place_order()
                logfix.info("Done: Put New Order\n")
                continue
            if options == '2':
                self.fixSession.place_open_limit_order()
                time.sleep(2)
                self.fixSession.get_order_status()
            if options == "3":
                sys.exit(0)
            else:
                time.sleep(2)