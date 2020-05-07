# coding: utf-8
import shutil
from filecmp import dircmp


# def print_diff_files(dcmp):
#     for name in dcmp.diff_files:
#         print("diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right))
#
#     for sub_dcmp in dcmp.subdirs.values():
#         print_diff_files(sub_dcmp)
# # print_diff_files(dcmp)
import os

old_path = r'E:\AllProject\MyProject\Upatch-tool\ant-module-discovery'
new_path = r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery'
dcmp = dircmp(old_path, new_path)


def deal_diff_file(dcmp):
    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            print(error_info)
            new_file = os.path.join(dcmp.right, name)
            shutil.copy(new_file, dcmp.left)
    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp)


deal_diff_file(dcmp)


