# coding: utf-8

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, argv=None, help=True, version=None,
                       options_first=False)
    print(arguments)
