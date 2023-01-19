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

import quickfix as fix
import uuid

def create_header(portfolio_id, message_type):
    """Build FIX Message Header"""
    message = fix.Message()
    header = message.getHeader()
    header.setField(message_type)
    message.setField(fix.Account(portfolio_id))
    message.setField(fix.ClOrdID(str(uuid.uuid4())))
    return message

def build_user_logout_message(fixSession, sessionID):
    """Build Cancel Order Message (F) based-on user input"""
    logout_message = fix.Message()
    header = logout_message.getHeader()
    header.setField(fix.MsgType(fix.MsgType_Logout))
    fixSession.send_message(logout_message)
    time.sleep(2)
    sys.exit()