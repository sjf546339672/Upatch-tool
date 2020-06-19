# coding: utf-8
from collections import OrderedDict

import datetime
yaml_path = "E:\Uyun-python\Upatch-tool\platform-ant\patch.yaml"

year = datetime.datetime.now().year
month = datetime.datetime.now().month
day = datetime.datetime.now().day


data = {
    "name": "1111111",
    "current_module_version": "1111111",
    "patched_module_version": "1111111"
}
from ruamel.yaml import YAML

yaml = YAML(typ='safe')
dict1 = {
    'release_time': datetime.date(year, month, day),
    "target_modules": [data]
}


fw = open(yaml_path, mode='w')
yaml.dump(dict1, fw)
fw.close()
