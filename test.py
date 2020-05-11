# coding: utf-8
import filecmp
import os
import shutil

import re

from upatch import create_dir, search_module_yaml, read_yaml, deal_upatch


def re_module_yaml_path(base_path, path):
    list1 = []
    for i in base_path.split("\\"):
        list1.append(i)
    test = "\\\\".join(list1)

    pattern = r"^{}\\[\s\S]*\\".format(test)
    pattern_result = re.findall(pattern, path)
    if pattern_result != []:
        list2 = []
        for i in pattern_result[0].split("\\"):
            list2.append(i)
        list2.pop()
        result = '\\'.join(list2)
    else:
        pattern1 = r"^{}\\[\s\S]+".format(test)
        result2 = re.findall(pattern1, path)
        result = result2[0]
    return result


def deal_module_yaml_folder(old_ant_uyun_path, dcmp):
    module_yaml_folder = re_module_yaml_path(old_ant_uyun_path, os.path.abspath(dcmp.left))
    old_module_yaml_path = os.path.join(module_yaml_folder, 'module.yaml')
    current_module_version = read_yaml(old_module_yaml_path)[0]
    new_module_yaml_path = search_module_yaml(dcmp.right, "module.yaml")
    module_name = read_yaml(new_module_yaml_path)[1]
    return module_name, current_module_version


def deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path,
                   patched_module_version):
    """旧包文件和新包文件进行比较"""
    if dcmp.right_only:
        for i in dcmp.right_only:
            whole_path = os.path.join(os.path.abspath(dcmp.right), i)
            file_path = dcmp.right.split(new_ant_uyun_path)[1]
            splice_path = patch_path + file_path
            create_dir(splice_path)
            shutil.copy(whole_path, splice_path)

            try:
                deal_result = deal_module_yaml_folder(old_ant_uyun_path, dcmp)
                deal_upatch(patch_path, deal_result[0], deal_result[1],
                            patched_module_version)
            except Exception as e:
                print(e)

    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            new_file = os.path.join(dcmp.right, name)
            file_path = dcmp.right.split(new_ant_uyun_path)[1]
            splice_path = patch_path+file_path
            create_dir(splice_path)
            shutil.copy(new_file, splice_path)

            try:
                deal_result = deal_module_yaml_folder(old_ant_uyun_path, dcmp)
                deal_upatch(patch_path, deal_result[0], deal_result[1],
                            patched_module_version)
            except Exception as e:
                print(e)

    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path, patched_module_version)


old_ant_uyun_path = os.path.join(os.getcwd(), 'old_uyun')
new_ant_uyun_path = os.path.join(os.getcwd(), 'new_uyun')
patch_path = os.path.join(os.getcwd(), 'patch')
patched_module_version = "2.0.16.41"

dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)

deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path, patched_module_version)
