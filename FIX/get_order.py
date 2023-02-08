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
import sys
import quickfix
from Model.configuration import Configuration
import configparser
from orders import Orders

config = configparser.ConfigParser()


def main():
    """Main"""
    try:
        Configuration().build_config()
        settings = quickfix.SessionSettings('example.cfg', True)

        orders_workshop = Orders()

        storefactory = quickfix.FileStoreFactory(settings)
        logfactory = quickfix.FileLogFactory(settings)
        initiator = quickfix.SSLSocketInitiator(orders_workshop, storefactory, settings, logfactory)

        initiator.start()
        orders_workshop.run_get_order()

    except (quickfix.ConfigError, quickfix.RuntimeError):

        sys.exit()


if __name__ == '__main__':
    main()
