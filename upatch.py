# coding: utf-8
import tarfile
import os
import re

package = r"E:\AllProject\MyProject\Upatch\UYUN-Ant.tar.gz"
regex = re.compile("[\s\S]*.gz$")
list_path = []


def decompresession(path):
    files = tarfile.open(path)
    files.extractall(os.getcwd())
    return os.getcwd()


def regular_path(path):
    regex = re.compile("[\s\S]*.gz$")
    if regex.findall(path):
        path = decompresession(path)
        all_file_path(path)


def all_file_path(path):
    for root, folders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.findall(file_path):
                path = decompresession(file_path)
                all_file_path(path)
            else:
                list_path.append(file_path)
        for folder in folders:
            folder_path = os.path.join(root, folder)
            all_file_path(folder_path)


path = decompresession(package)
all_file_path(path)
# for i in list(set(list_path)):
#     print(i)









