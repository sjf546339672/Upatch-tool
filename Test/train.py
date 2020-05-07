# coding: utf-8
import copy
import filecmp

import os
import shutil

import time

old_path = r'E:\AllProject\MyProject\Upatch-tool\Test\index2.py'
new_path = r'E:\AllProject\MyProject\Upatch-tool\NewTest\index2.py'

if not filecmp.cmp(old_path, new_path):
    print("文件内容不同")
    os.remove(old_path)
    time.sleep(15)
    shutil.copy(new_path, os.path.abspath(os.path.dirname(old_path)))
else:
    print("文件内容相同")


