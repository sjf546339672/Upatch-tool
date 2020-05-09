# coding: utf-8
import os

import re

test1 = r'E:\AllProject\MyProject\Upatch-tool\new-ant-uyun\platform-ant-dispatcher\bin'
test2 = r'E:\\AllProject\\MyProject\\Upatch-tool\\new-ant-uyun'

t = r'{}'.format(test2)
n = re.findall(t, test1)
print(n)