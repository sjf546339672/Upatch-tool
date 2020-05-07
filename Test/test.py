# coding: utf-8

# test = ['hello', 'world', 'nihao', 'thanks', 'you']
# test1 = ['hello', 'thanks', 'you', 'world', 'nihao']
# for i in test:
#     if i in test1:
#         print(i)
#         index = test1.index(i)
import os

test = r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery\packages\remote-discovery\discovery\deepscan\storage\raid\smis\hp\new_par.bdp'
test1 = [
r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery\packages\remote-discovery\discovery\deepscan\storage\raid\smis\hp\new_par.bdp',
r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery\packages\remote-discovery\discovery\deepscan\storage\raid\smis\hp\new_par.bd',
r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery\packages\remote-discovery\discovery\deepscan\storage\raid\smis\hp\new_par.b',
r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\ant-module-discovery\packages\remote-discovery\discovery\deepscan\storage\raid\smis\hp\new_par.bl',
]

file_name = os.path.basename(test)

for i in test1:
    if file_name in i:
        print(1111)
        print(i)