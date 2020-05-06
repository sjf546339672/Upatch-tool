# coding: utf-8

# """LiXiang
# Usage:
#     li_xiang tcp
# Options:
#   -h --help     帮助
#   -v --version     查看版本号
# """
# from docopt import docopt
#
# if __name__ == '__main__':
#     arguments = docopt(__doc__, argv=None, help=True, version=None,
#                        options_first=False)
#     print(arguments)


import os

import re

file_path = r'E:\AllProject\MyProject\Upatch\file1'
test1 = r"ant-module-discovery/packages"
print(os.path.join(file_path, test1))
file = os.path.join(file_path, test1)
if os.path.isdir(file):
    print(11111)
else:
    print(22222)




# coding: utf-8
import tarfile
import os

base_path = os.path.join(os.getcwd(), 'file1')
print(base_path)


def decompresession(file_path):
    files = tarfile.open(file_path)
    files.extractall(path=file_path)
    for file in files:
        if os.path.isdir(os.path.join(base_path, file.name)):
            print(file.name, 111)
        else:
            print(file.name, 222)


def all_files_path(rootDir):
    for root, dirs, files in os.walk(rootDir):     # 分别代表根目录、文件夹、文件
        for file in files:                         # 遍历文件
            file_path = os.path.join(root, file)   # 获取文件绝对路径
            filepaths.append(file_path)            # 将文件路径添加进列表
        for dir in dirs:                           # 遍历目录下的子目录
            dir_path = os.path.join(root, dir)     # 获取子目录路径
            all_files_path(dir_path)               # 递归调用


if __name__ == "__main__":
    dirpath = r'E:\AllProject\MyProject\Upatch\file1'
    filepaths = []                                 # 初始化列表用来
    all_files_path(dirpath)
    with open('dir.txt', 'a') as f:
        for filepath in filepaths:
            f.write(filepath + '\n')


def decompresession1(file1_path):
    files = tarfile.open(file1_path)
    files.extractall(path=file_path)
    for file in files:
        if file.isdir():
            for i in file:
                print(i)
        else:
            regex = re.compile("[\s\S]*.gz$")
            if regex.findall(file.name):
                pass
                # print(regex.findall(file.name))
        # print(file.name, file.isdir())
        # print(os.path.join(os.getcwd(), file.name))
        # if os.path.isdir(os.path.join(os.getcwd(), file.name)):
        #     print(file.name, 111)
        # else:
        #     print(file.name, 222)