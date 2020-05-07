# coding: utf-8
import tarfile
import os
import re
import shutil
import filecmp

old_package_path = r'E:\AllProject\MyProject\Upatch-tool\UYUN-Ant.tar.gz'
new_package_path = r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\UYUN-Ant.tar.gz'

list_path = []
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
            else:
                list_path.append(file_path)
        for folder in folders:
            folder_path = os.path.join(root, folder)
            all_file_path(folder_path)


def all_file_path_list(package_path, save_path):
    all_path = []
    path = untar(package_path, save_path)
    all_file_path(path)
    for i in list(set(list_path)):
        all_path.append(i)
    del list_path[(-(len(list_path))):]
    return all_path


def deal_file(old_package_path, new_package_path):
    old_list = all_file_path_list(old_package_path,
                                  os.path.abspath(os.path.dirname(old_package_path)))

    new_list = all_file_path_list(new_package_path,
                                  os.path.abspath(os.path.dirname(new_package_path)))

    if len(old_list) == len(new_list):
        for new_path in new_list:
            file_name = os.path.basename(new_path)
            print(file_name)
            # print(new_path, old_list[index])
            # if new_path in old_list:
            #     index = old_list.index(new_path)
            #     old_path = old_list[index]
            #     if not filecmp.cmp(new_path, old_path):
            #         os.remove(old_path)
            #         shutil.copy(new_path, os.path.abspath(os.path.dirname(old_path)))
    elif len(old_list) < len(new_list):
        pass
    elif len(old_list) > len(new_list):
        pass


deal_file(old_package_path, new_package_path)
