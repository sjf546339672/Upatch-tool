# coding: utf-8
import shutil
from filecmp import dircmp
import os

import sys

old_path = r'E:\AllProject\MyProject\Upatch-tool\ant-module-discovery'
new_path = r'E:\AllProject\MyProject\Upatch-tool\ant-uyun\ant-module-discovery'
dcmp = dircmp(old_path, new_path)


def deal_diff_file(dcmp):
    for i in dcmp.right_list:
        if i not in dcmp.left_list:
            whole_path = os.path.join(os.path.abspath(dcmp.right), i)
            print(whole_path)

    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            new_file = os.path.join(dcmp.right, name)
            print("----->", dcmp.right, name)
            print(os.path.abspath(os.path.dirname(sys.argv[0])))
            shutil.copy(new_file, patch_path)

    for sub_dcmp in dcmp.subdirs.values():  #
        deal_diff_file(sub_dcmp)


patch_path = os.path.join(os.getcwd(), 'patch')
if not os.path.isdir(patch_path):
    os.mkdir(patch_path)

deal_diff_file(dcmp)





