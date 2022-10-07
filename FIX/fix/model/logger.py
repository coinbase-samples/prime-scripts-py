import logging


def setup_logger(logger_name, log_file, level=logging.INFO):
    lz = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d : %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    lz.setLevel(level)
    lz.addHandler(fileHandler)

    '''To output logs to the terminal, uncomment the following lines:'''
    # streamHandler = logging.StreamHandler()
    # streamHandler.setFormatter(formatter)
    # lz.addHandler(streamHandler)