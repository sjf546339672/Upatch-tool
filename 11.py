# # coding: utf-8
# import re
#
#
# def re_module_yaml_path(base_path, path):
#     """通过正则匹配出module.yaml文件路径"""
#     list1 = []
#     for i in base_path.split("\\"):
#         list1.append(i)
#     test = "\\\\".join(list1)
#
#     pattern = r"^{}\\[\s\S]*?\\".format(test)
#     pattern_result = re.findall(pattern, path)
#     print(pattern_result)
#     if pattern_result != []:
#         print(11111)
#         list2 = []
#         for i in pattern_result[0].split("\\"):
#             list2.append(i)
#         list2.pop()
#         result = '\\'.join(list2)
#     else:
#         print(22222)
#         pattern1 = r"^{}\\[\s\S]+".format(test)
#         result2 = re.findall(pattern1, path)
#         result = result2[0]
#     return result
#
#
# base_path = r"E:\AllProject\MyProject\Upatch-tool\old_uyun"
# path = r"E:\AllProject\MyProject\Upatch-tool\old_uyun\platform-ant-fs\conf\disconf"
# print(re_module_yaml_path(base_path, path))
import filecmp

import os

ROOT_PATH = r'E:\AllProject\MyProject\Upatch-tool\new_uyun'
# 输入参数
ignore = [r'platform-ant-dispatcher\uninstall.sh', 'platform-ant-fs\conf\disconf']
# 使用数据结构（使用dict即可）格式化后
ignore_map = {
    '\platform-ant-dispatcher': ['uninstall.sh'],
    '\platform-ant-fs\conf': ['disconf'],
}

dcmp = filecmp.dircmp(r"E:\AllProject\MyProject\Upatch-tool\old_uyun",
                      r"E:\AllProject\MyProject\Upatch-tool\new_uyun")


def files(dcmp):
    relative_path = dcmp.right.split(ROOT_PATH)
    print(relative_path)
    if relative_path[1] in ignore_map:
        print(relative_path[1])
    #     dcmp.ignore = ignore_map[relative_path[1]]
    #
    # # print('right only: {}'.format(dcmp.right_only))
    # for i in dcmp.diff_files:
    #     pass
    #     # print(os.path.join(ROOT_PATH, i))
    #
    # for sub_dcmp in dcmp.subdirs.values():
    #     files(sub_dcmp)


files(dcmp)






