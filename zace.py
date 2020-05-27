# coding: utf-8
import copy
import json
import yaml
description = "自动发现后端服务模块;Discovery Server"
yaml_path = r"E:\Uyun-python\Upatch-tool\test.yaml"


def check_contain_chinese(check_str):
    for ch in str(check_str).decode("utf-8"):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def deal_chinese(param):
    result = check_contain_chinese(param)
    if result is True:
        t = json.loads(json.dumps(param))
        return t
    return param


def write_patch(path, description):
    if description is not None:
        result = description.split(";")
        for i in result:
            fp = open(path, mode="r")
            yarn_content = fp.read()
            res = yaml.load(yarn_content)
            if "description" in res.keys():
                fw = open(path, "w")
                new_res = copy.deepcopy(res)
                new_res["description"].append(deal_chinese(i))
                res.clear()
                yaml.dump(new_res, fw, allow_unicode=True)
                fw.close()
            else:
                fn = open(path, "a")
                data = {"description": [deal_chinese(i)]}
                yaml.dump(data, fn, allow_unicode=True)
                fn.close()


write_patch(yaml_path, description)