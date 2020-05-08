# coding: utf-8


import tarfile
import os
import re
import shutil
import filecmp
from docopt import docopt

old_package_path = r'E:\AllProject\MyProject\Upatch-tool\UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz'
regex = re.compile("[\s\S]*.gz$")


def untar(path, save_path):
    """解压压缩文件"""
    try:
        tar = tarfile.open(path)
        tar.extractall(save_path)
    except Exception as e:
        print(e)


def all_file_path(path):
    for root, folders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.findall(file_path):
                current_path = os.path.abspath(os.path.dirname(file_path))
                untar(file_path, current_path)
                os.remove(file_path)
        for folder in folders:
            folder_path = os.path.join(root, folder)
            all_file_path(folder_path)


def main():
    old_ant_uyun_path = os.path.join(os.getcwd(), 'new-ant-uyun')
    if not old_ant_uyun_path:
        os.mkdir(old_ant_uyun_path)
    untar(old_package_path, old_ant_uyun_path)
    all_file_path(old_ant_uyun_path)


if __name__ == '__main__':
    main()
