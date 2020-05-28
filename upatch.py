# -*- coding: utf-8 -*-
"""
Usage:
  upatch.py <old_package_path> <new_package_path> -o <output> [-i <ignore>...] [options]

Options:
  -d description --description=description  message,
"""
import json
import os
import re

import chardet
import yaml
import copy
import shutil
import filecmp
import tarfile
import datetime
import platform
from docopt import docopt
from collections import OrderedDict

regex = re.compile("[\s\S]*.gz$")


def untar(path, save_path):
    """解压压缩文件"""
    try:
        tar = tarfile.open(path)
        tar.extractall(save_path)
    except Exception as e:
        print(e)


def read_yaml(module_yaml_path):
    """读取yaml文件获取version"""
    yaml.warnings({"YAMLLoadWarning": False})
    fp = open(module_yaml_path, 'r')
    result = fp.read()
    dict_yaml = yaml.load(result)
    version = dict_yaml['version']
    module_name = dict_yaml['name']
    return version, module_name


def all_file_path(path):
    """文件夹中存在tar.gz文件再进行解压"""
    for root, folders, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.findall(file_path):
                current_path = os.path.abspath(os.path.dirname(file_path))
                untar(file_path, current_path)
                os.remove(file_path)


def create_dir(path):
    """递归创建目录"""
    if not os.access(path, os.R_OK):
        path_last = len(path)-1
        if path[path_last] == '/' or path[path_last] == '\\':
            path = path[0:path_last]

        create_dir(os.path.dirname(path))

        if not os.path.isfile(path):
            os.mkdir(path)


def re_version(str_version):
    """正则匹配version字符串"""
    pattern = r'\d+'
    result = re.findall(pattern, str_version)
    new_version = '.'.join(result)
    return new_version


def patch_package(output_filename, source_dir):
    """对文件夹进行打包"""
    try:
        with tarfile.open(output_filename + '.tar.gz', "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        # shutil.rmtree(source_dir)
        return True
    except Exception as e:
        print(e)
        return False


def get_untar_name(old_list, new_list):
    """获取解压之后的文件名"""
    for j in old_list:
        if j in new_list:
            new_list.remove(j)
    return new_list[0]


def get_all_files(package_path, save_path):
    untar(package_path, save_path)
    all_file_path(save_path)
    return save_path


def deal_upatch(patch_path, module_name, current_module_version, patched_module_version):
    """向patch.yaml文件中添加数据"""
    yaml_path = os.path.join(patch_path, 'patch.yaml')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    if not os.path.exists(yaml_path):
        fd = open(yaml_path, mode="w")
        fd.close()
    fp = open(yaml_path, mode="r")
    yarn_content = fp.read()
    res = yaml.load(yarn_content)
    if not res:
        fw = open(yaml_path, mode='w')
        dict1 = OrderedDict()
        dict1["name"] = module_name
        dict1["current_module_version"] = current_module_version
        dict1["patched_module_version"] = patched_module_version
        data = {
            'release_time': datetime.date(year, month, day),
            'target_modules': [{i: k} for i, k in dict1.items()]
        }
        yaml.dump(data, fw)
    else:
        fn = open(yaml_path, 'w')
        list1 = [i for i in res.keys()]
        if module_name not in list1:
            fn = open(yaml_path, 'w')
            dict1 = OrderedDict()
            dict1["name"] = module_name
            dict1["current_module_version"] = current_module_version
            dict1["patched_module_version"] = patched_module_version
            res['release_time'] = datetime.date(year, month, day)
            res['target_modules'] = [{i: k} for i, k in dict1.items()]
        yaml.dump(res, fn)
    fp.close()


def test(base_path, path):
    if platform.system().lower() == "windows":
        result = path.split(base_path)[1].split('\\')[1]
        folder_path = os.path.join(base_path, result)
    else:
        result = path.split(base_path)[1].split('/')[1]
        folder_path = os.path.join(base_path, result)
    return folder_path


def module_yaml_path(base_path, path):
    """匹配出module.yaml文件路径"""
    folder_path = test(base_path, path)
    if "module.yaml" in os.listdir(folder_path):
        old_path = folder_path
    else:
        result_path = test(folder_path, path)
        old_path = result_path
    return old_path


def deal_module_yaml_folder(old_ant_uyun_path, dcmp):
    """获取模块名和旧包yaml中的版本号"""
    module_yaml_folder = module_yaml_path(old_ant_uyun_path, os.path.abspath(dcmp.left))
    old_module_yaml_path = os.path.join(module_yaml_folder, 'module.yaml')
    current_module_version = read_yaml(old_module_yaml_path)[0]
    module_name = read_yaml(old_module_yaml_path)[1]
    return module_name, current_module_version


def deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path,
                   patched_module_version, ignore_maps):
    """旧包文件和新包文件进行比较"""
    relative_path = dcmp.right.split(new_ant_uyun_path)
    relative_path_result = relative_path[1][1:]

    if relative_path_result in ignore_maps:
        dcmp.ignore = ignore_maps[relative_path_result]

    dcmp.diff_files += dcmp.right_only
    for i in dcmp.diff_files:
        whole_path = os.path.join(dcmp.right, i)
        file_path = os.path.join(patch_path, relative_path_result)
        create_dir(file_path)
        shutil.copy(whole_path, file_path)
        try:
            deal_result = deal_module_yaml_folder(old_ant_uyun_path, dcmp)
            deal_upatch(patch_path, deal_result[0], deal_result[1],
                        patched_module_version)
        except Exception as e:
            print(e)

    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, old_ant_uyun_path,
                       patch_path, patched_module_version, ignore_maps)


def deal_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)


def write_patch(path, description):
    if description is not None:
        if len(description) != 0:
            coding = chardet.detect(description)["encoding"]
            content = description.decode(coding).encode('utf8')
            result = content.split(";")
            for i in result:
                fp = open(path, mode="r")
                yarn_content = fp.read()
                res = yaml.load(yarn_content)

                if "description" in res.keys():
                    fw = open(path, mode="w")
                    new_res = copy.deepcopy(res)
                    new_res["description"].append(i)
                    res.clear()
                    yaml.safe_dump(new_res, fw, default_flow_style=False, encoding="utf-8", allow_unicode=True)
                    fw.close()
                else:
                    fn = open(path, "a")
                    data = {"description": [i]}
                    yaml.safe_dump(data, fn, default_flow_style=False, encoding="utf-8", allow_unicode=True)
                    fn.close()


def deal_file(old_package_path, new_package_path, new_version, ignore_maps, description):
    """获取处理压缩包"""
    patch_path = os.path.join(os.getcwd(), 'patch')
    old_folders = os.path.join(os.getcwd(), 'old_folders')
    new_folders = os.path.join(os.getcwd(), 'new_folders')
    deal_folder(patch_path)
    deal_folder(old_folders)
    deal_folder(new_folders)

    try:
        old_ant_uyun_path = get_all_files(old_package_path, old_folders)
        new_ant_uyun_path = get_all_files(new_package_path, new_folders)
        dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)
        deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path,
                       patch_path, new_version, ignore_maps)
        path = os.path.join(patch_path, "patch.yaml")
        write_patch(path, description)
        patch_package('patch', patch_path)
    except Exception as e:
        print(e)


def main():
    args = docopt(__doc__)
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    output = args['<output>']
    new_version = re_version(output)
    ignore_list = args['<ignore>']
    description = args["--description"]
    ignore_maps = {}
    for ignore in ignore_list:
        if os.path.dirname(ignore) in ignore_maps:
            if os.path.basename(ignore) not in ignore_maps[os.path.dirname(ignore)]:
                ignore_maps[os.path.dirname(ignore)].append(os.path.basename(ignore))
        else:
            ignore_maps[os.path.dirname(ignore)] = [os.path.basename(ignore)]
    deal_file(old_package_path, new_package_path, new_version, ignore_maps, description)


if __name__ == '__main__':
    main()
