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
import sys, os
import argparse
import quickfix
from application import Application
from config import Configuration
# import certifi
import configparser

config = configparser.ConfigParser()


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

    except (quickfix.ConfigError, quickfix.RuntimeError):

        sys.exit()


if __name__ == '__main__':
    main()
