
class Options:
    def __init__(self):
        pass

    def print_options(self, args):
        for key in args:
            print(f"\t{key}\t\t\t{args[key]}")
