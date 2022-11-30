import sys, os
import argparse
import quickfix
from application import Application
from config import Configuration
import certifi
import configparser

config = configparser.ConfigParser()
config.read('fix/resources/prime.properties')

def main():
    """Main"""
    try:
        Configuration().build_config()
        settings = quickfix.SessionSettings('example.cfg', True)
        application = Application()
        storefactory = quickfix.FileStoreFactory(settings)
        logfactory = quickfix.FileLogFactory(settings)
        initiator = quickfix.SSLSocketInitiator(application, storefactory, settings, logfactory)

        initiator.start()
        application.run()

    except (quickfix.ConfigError, quickfix.RuntimeError) as e:
        sys.exit()

if __name__=='__main__':
    main()


