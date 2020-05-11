# coding: utf-8
import re

test1 = r"E:\AllProject\MyProject\Upatch-tool\new_uyun\platform-ant-executor\agent"
test3 = r"E:\AllProject\MyProject\Upatch-tool\new_uyun\platform-ant-executor"
test2 = r"E:\AllProject\MyProject\Upatch-tool\new_uyun"

test5 = test3


def re_module_yaml_path():
    list1 = []
    for i in test2.split("\\"):
        list1.append(i)
    test = "\\\\".join(list1)

    pattern = r"^{}\\[\s\S]*\\".format(test)
    pattern_result = re.findall(pattern, test5)
    if pattern_result != []:
        list2 = []
        for i in pattern_result[0].split("\\"):
            list2.append(i)
        list2.pop()
        result = '\\'.join(list2)
    else:
        pattern1 = r"^{}\\[\s\S]+".format(test)
        result2 = re.findall(pattern1, test5)
        result = result2[0]
    return result


print(re_module_yaml_path())