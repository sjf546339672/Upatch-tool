# coding: utf-8

"""LiXiang
Usage:
    li_xiang tcp
Options:
  -h --help     帮助
  -v --version     查看版本号
"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, argv=None, help=True, version=None,
                       options_first=False)
    print(arguments)
