# coding: utf-8
import datetime

year = datetime.datetime.now().year
month = datetime.datetime.now().month
day = datetime.datetime.now().day
release_time = datetime.date(year, month, day)
# 'target_modules': [{"name": 1111111, "current_module_version": 111111, "patched_module_version": 1111111}]
yaml_doc = """
release_time: {}
target_modules:
  - name: {}
    current_module_version: {}
    patched_module_version: {}
""".format(release_time, 111, 111, 111)
from ruamel.yaml import YAML, sys, os

yaml = YAML()
data = yaml.load(yaml_doc)
yaml_path = "F:\Myproject\Upatch-tool\platform-ant\patch.yaml"

if not os.path.exists(yaml_path):
    with open(yaml_path, 'w+') as outfile:
        yaml.dump(data, outfile)
else:
    import ruamel.yaml
    with open(yaml_path, 'r') as ft:
        all_data = ruamel.yaml.safe_load(ft)
    if all_data is None:
        with open(yaml_path, 'w+') as outfile:
            yaml.dump(data, outfile)
    else:
        import ruamel.yaml
        module_name = "discovery-web"
        current_module_version = "1111111111111"
        patched_module_version = "1111111111111"
        with open(yaml_path, 'r') as ft:
            all_data = ruamel.yaml.safe_load(ft)
            list_name = []
            for i in all_data['target_modules']:
                list_name.append(i['name'])
            if module_name not in list_name:
                all_data['target_modules'].append({"name": module_name, "current_module_version": current_module_version, "patched_module_version": patched_module_version})
                print(all_data)
                with open(yaml_path, 'w') as fm:
                    yaml.dump(all_data, fm)


