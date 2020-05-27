# coding: utf-8
"""
Usage:
  upatch.py <old_package_path> <new_package_path> -o <output> [-i <ignore>...] [options]

Options:
  -d description --description=description  message,
"""
from docopt import docopt


def main():
    args = docopt(__doc__)
    import chardet
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    output = args['<output>']
    description = args["--description"]
    coding = chardet.detect(description)["encoding"]
    content = description.decode(coding).encode('utf8')


if __name__ == '__main__':
    main()