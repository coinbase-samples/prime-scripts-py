import logging

loggers = {}

def setup_logger(logger_name, log_file, level=logging.INFO):
    global loggers

    if loggers.get(logger_name):
        return loggers.get(logger_name)

    else:
        lz = logging.getLogger(logger_name)
        lz.setLevel(level)
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d : %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        lz.addHandler(streamHandler)

        loggers[logger_name] = lz
        return lz


def format_message(message):
    msg = message.toString().replace('\u0001', '|')
    return msg


