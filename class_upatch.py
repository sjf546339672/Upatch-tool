# coding: utf-8

"""
Usage:
  upatch.py upatch <old_package_path> <new_package_path>
  upatch.py (-h | --help)
  upatch.py (-v | --version)

Arguments:
  suffix_name name suffix
  names       many names

Options:
  -h --help            Show this screen.
  -v --version         Show version.

"""

import tarfile
import os
import re
import shutil
import filecmp
from docopt import docopt

# old_package_path = r'E:\AllProject\MyProject\Upatch-tool\old-ant-uyun\UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz'
# new_package_path = r'E:\AllProject\MyProject\Upatch-tool\new-ant-uyun\UYUN-Platform-Ant-V2.0.R16.41-all.tar.gz'

regex = re.compile("[\s\S]*.gz$")


def untar(path, save_path):
    """解压压缩文件"""
    try:
        tar = tarfile.open(path)
        tar.extractall(save_path)
        tar_path = os.path.join(save_path, tar.getnames()[0])
        return tar_path
    except Exception as e:
        print(e)


def all_file_path(path):
    for root, folders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.findall(file_path):
                current_path = os.path.abspath(os.path.dirname(file_path))
                path = untar(file_path, current_path)
                all_file_path(path)
                os.remove(file_path)
        for folder in folders:
            folder_path = os.path.join(root, folder)
            all_file_path(folder_path)


def all_file_path_list(package_path, save_path):
    path = untar(package_path, save_path)
    all_file_path(path)
    return path


def deal_diff_file(dcmp):
    for i in dcmp.left_list:
        if i not in dcmp.right_list:
            whole_path = os.path.join(os.path.abspath(dcmp.left), i)
            os.remove(whole_path)
    for j in dcmp.right_list:
        if j not in dcmp.left_list:
            whole_path = os.path.join(os.path.abspath(dcmp.right), j)
            shutil.copy(whole_path, os.path.abspath(dcmp.left))

    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            new_file = os.path.join(dcmp.right, name)
            shutil.copy(new_file, dcmp.left)
    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp)


def deal_file(old_package_path, new_package_path):
    old_path = all_file_path_list(
        old_package_path, os.path.abspath(os.path.dirname(old_package_path)))
    new_path = all_file_path_list(
        new_package_path, os.path.abspath(os.path.dirname(new_package_path)))
    dcmp = filecmp.dircmp(old_path, new_path)
    deal_diff_file(dcmp)


def main():
    args = docopt(__doc__, version='0.0.1')
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    print("============================")
    print(old_package_path, type(old_package_path))
    print(new_package_path, type(new_package_path))
    print("============================")
    deal_file(old_package_path, new_package_path)


if __name__ == '__main__':
    main()





