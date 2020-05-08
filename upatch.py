# coding: utf-8

import tarfile
import os
import re
import shutil
import filecmp
from docopt import docopt

old_package_path = r'E:\AllProject\MyProject\Upatch-tool\UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz'
new_package_path = r'E:\AllProject\MyProject\Upatch-tool\UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz'
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


def deal_diff_file(dcmp):
    for j in dcmp.right_list:
        if j not in dcmp.left_list:
            whole_path = os.path.join(os.path.abspath(dcmp.right), j)
            print(whole_path)

    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            new_file = os.path.join(dcmp.right, name)
            print(new_file)
    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp)


def deal_file(old_package_path, new_package_path):
    old_ant_uyun_path = os.path.join(os.getcwd(), 'old-ant-uyun')
    new_ant_uyun_path = os.path.join(os.getcwd(), 'new-ant-uyun')
    if not old_ant_uyun_path:
        os.mkdir(old_ant_uyun_path)
    if not new_ant_uyun_path:
        os.mkdir(new_ant_uyun_path)
    untar(old_package_path, old_ant_uyun_path)
    print("1111111111111")
    all_file_path(old_ant_uyun_path)
    print("2222222222222")
    untar(new_package_path, new_ant_uyun_path)
    print("3333333333333")
    all_file_path(new_ant_uyun_path)
    print("4444444444444")
    dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)


def main():
    deal_file(old_package_path, new_package_path)


if __name__ == '__main__':
    main()
