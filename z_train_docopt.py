# coding: utf-8
"""
Usage:
   {params} <old_package_path> <new_package_path> -o <output> [-i <ignore> <ignore>]
   {params} (-h | --help)
   {params} (-v | --version)

Options:
  -h, --help      显示帮助信息
  -i, --ignore   忽略目录或文件（可选，忽略的目录或文件不会放入补丁包中）
"""
import re
import shutil
import tarfile

import os
from docopt import docopt

# upatch old.tar.gz new.tar.gz
# -o ${扩展部分}-产品名-版本-patch.tar.gz UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz
# -i platform-ant-lss/lib/test.conf


def re_version(filename):
    pattern = r'\d+'
    result = re.findall(pattern, filename)
    new_version = '.'.join(result)
    return new_version


def untar(path, save_path):
    """解压压缩文件"""
    try:
        tar = tarfile.open(path)
        tar.extractall(save_path)
    except Exception as e:
        print(e)


def patch_package(output_filename, source_dir, ignore_list):
    for root, folders, files in os.walk(source_dir):
        for file in files:
            for i in ignore_list:
                if i in os.path.join(root, file):
                    os.remove(os.path.join(root, file))
        for folder in folders:
            for i in ignore_list:
                if i in os.path.join(root, folder):
                    shutil.rmtree(os.path.join(root, folder))
    try:
        with tarfile.open(output_filename + '.tar.gz', "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        shutil.rmtree(source_dir)
        return True
    except Exception as e:
        print(e)
        return False


def main():
    args = docopt(__doc__, version='0.0.1')
    print(args)
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    ignore_list = args['<ignore>']
    output = args['<output>']
    version = re_version(output)
    source_dir = os.path.join(os.getcwd(), 'patch')
    output_filename = os.path.basename(source_dir)
    patch_package(output_filename, source_dir, ignore_list)


if __name__ == '__main__':
    main()
