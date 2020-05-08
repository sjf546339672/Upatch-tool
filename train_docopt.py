# coding: utf-8

"""
Usage:
  train_docopt.py <old_package_path> <new_package_path>
  train_docopt.py (-h | --help)
  train_docopt.py (-v | --version)

Arguments:
  suffix_name name suffix
  names       many names

Options:
  -h --help            Show this screen.
  -v --version         Show version.
"""
from docopt import docopt


def main():
    args = docopt(__doc__, version='0.0.1')
    print(args['<old_package_path>'])
    print(args['<new_package_path>'])


if __name__ == '__main__':
    main()
