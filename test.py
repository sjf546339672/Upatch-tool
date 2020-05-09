# coding: utf-8
import shutil
import tarfile
from filecmp import dircmp
import os

import datetime

import re
import yaml
import sys

old_path = r'E:\AllProject\MyProject\Upatch-tool\old-ant-uyun'
new_path = r'E:\AllProject\MyProject\Upatch-tool\new-ant-uyun'
dcmp = dircmp(old_path, new_path)


def create_dir(path):
    if not os.access(path, os.R_OK):
        path_last = len(path)-1
        if path[path_last] == '/' or path[path_last] == '\\':
            path = path[0:path_last]

        create_dir(os.path.dirname(path))

        if not os.path.isfile(path):
            os.mkdir(path)


def search_module_yaml(root, target):
    items = os.listdir(root)
    if target in items:
        module_path = os.path.join(root, target)
        return module_path
    else:
        list1 = []
        t = root.split('\\')
        t.pop()
        for i in t:
            list1.append(i)
        path = '\\'.join(list1)
        try:
            return search_module_yaml(path, target)
        except Exception as e:
            print(e)


def read_yaml(module_yaml_path):
    fp = open(module_yaml_path, 'r', encoding="utf-8")
    result = fp.read()
    dict_yaml = yaml.load(result)
    version = dict_yaml['version']
    module_name = dict_yaml['name']
    return version, module_name


def deal_diff_file(dcmp, new_ant_uyun_path, patch_path, old_ant_uyun_path):
    for i in dcmp.right_list:
        if i not in dcmp.left_list:
            print(dcmp.right)
            whole_path = os.path.join(os.path.abspath(dcmp.right), i)
            file_path = dcmp.right.split(new_ant_uyun_path)[1]
            splice_path = patch_path + file_path
            create_dir(splice_path)
            shutil.copy(whole_path, splice_path)

            old_module_yaml_path = search_module_yaml(dcmp.left, "module.yaml")
            current_module_version = read_yaml(old_module_yaml_path)[0]
            new_module_yaml_path = search_module_yaml(dcmp.right, "module.yaml")
            module_name = read_yaml(new_module_yaml_path)[1]
            patched_module_version = 'aaaaaaa'
            deal_upatch(patch_path, module_name, current_module_version, patched_module_version)

    for name in dcmp.diff_files:
        error_info = "diff_file {} found in {} and {}".format(name, dcmp.left, dcmp.right)
        if error_info:
            new_file = os.path.join(dcmp.right, name)
            file_path = dcmp.right.split(new_ant_uyun_path)[1]
            splice_path = patch_path+file_path
            create_dir(splice_path)
            shutil.copy(new_file, splice_path)

            old_module_yaml_path = search_module_yaml(dcmp.left, "module.yaml")
            current_module_version = read_yaml(old_module_yaml_path)[0]
            new_module_yaml_path = search_module_yaml(dcmp.right, "module.yaml")
            module_name = read_yaml(new_module_yaml_path)[1]
            patched_module_version = 'aaaaaaa'
            deal_upatch(patch_path, module_name, current_module_version, patched_module_version)
    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, patch_path, old_ant_uyun_path)


def deal_upatch(patch_path, module_name, current_module_version, patched_module_version):
    yaml_path = os.path.join(patch_path, 'patch1.yaml')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    if not os.path.exists(yaml_path):
        fd = open(yaml_path, mode="w", encoding="utf-8")
        fd.close()
    fp = open(yaml_path, encoding='utf-8')
    yarn_content = fp.read()
    res = yaml.load(yarn_content)
    print(res)
    if not res:
        fw = open(yaml_path, 'w', encoding='utf-8')
        data = {
            'release_time': datetime.date(year, month, day),
            'target_modules': [
                {'a-name': module_name,
                 'current_module_version': current_module_version,
                 'patched_module_version': patched_module_version}
            ],
        }
        yaml.dump(data, fw)
    else:
        list1 = []
        for i in res['target_modules']:
            list1.append(i['a-name'])
        if not module_name in list1:
            fn = open(yaml_path, 'w', encoding='utf-8')
            res['release_time'] = datetime.date(year, month, day)
            res['target_modules'].append(
                {'a-name': module_name,
                 'current_module_version': current_module_version,
                 'patched_module_version': patched_module_version})
            yaml.dump(res, fn)
    fp.close()


# 一次性打包整个根目录。空子目录会被打包。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


# 逐个添加文件打包，未打包空子目录。可过滤文件。
# 如果只打包不压缩，将"w:gz"参数改为"w:"或"w"即可。
def make_targz_one_by_one(output_filename, source_dir):
    tar = tarfile.open(output_filename, "w:gz")
    for root, dir, files in os.walk(source_dir):
        for file in files:
            pathfile = os.path.join(root, file)
            tar.add(pathfile)
    tar.close()


def patch_package(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def main():
    patch_path = os.path.join(os.getcwd(), 'patch')
    if not os.path.isdir(patch_path):
        os.mkdir(patch_path)
    # patch_path = os.path.join(os.getcwd(), 'patch')
    # # module_name = 'platform-ant-dispatcher'
    # # deal_upatch(patch_path, module_name)
    #
    # new_ant_uyun_path = os.path.join(os.getcwd(), 'new-ant-uyun')
    # if not new_ant_uyun_path:
    #     os.mkdir(new_ant_uyun_path)
    # old_ant_uyun_path = os.path.join(os.getcwd(), 'old-ant-uyun')
    # if not new_ant_uyun_path:
    #     os.mkdir(old_ant_uyun_path)
    # deal_diff_file(dcmp, new_ant_uyun_path, patch_path, old_ant_uyun_path)
    patch_package('dsdasda.tar.gz', patch_path)


if __name__ == '__main__':
    main()

