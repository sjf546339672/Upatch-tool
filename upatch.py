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
import stat

import chardet
import yaml
import copy
import shutil
import filecmp
import tarfile
import datetime
import platform
import subprocess
from subprocess import Popen
from docopt import docopt

regex = re.compile("[\s\S]*.gz$")


def untar(path, save_path):
    """解压压缩文件"""
    try:
        tar = tarfile.open(path)
        tar.extractall(save_path)
    except Exception as e:
        print(e)


def get_package_name(tar_package_name):
    """获取包名"""
    pattern = r"-([\w\W]+)(-V)"
    package_name = re.findall(pattern, tar_package_name)[0][0].lower()
    return package_name


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
    output_filename = output_filename + '.tar.gz'
    get_cwd = os.getcwd()
    list1 = []
    file_list = os.listdir(source_dir)
    for item in file_list:
        list1.append(item)
    result = ' '.join(list1)
    cmd = "tar czvf {} {}".format(output_filename, result)
    output_filename_path = os.path.join(source_dir, output_filename)
    try:
        pg = Popen("cd {} && {}".format(source_dir, cmd),
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                   shell=True)
        buff, buffErr = pg.communicate()
        shutil.move(output_filename_path, get_cwd)
    except Exception as e:
        print (e)


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
    release_time = datetime.date(year, month, day)
    from ruamel.yaml import YAML
    yaml = YAML()
    if not os.path.exists(yaml_path):
        yaml_doc = """
        release_time: {}
        target_modules:
          - name: {}
            current_module_version: {}
            patched_module_version: {}
        """.format(release_time, module_name, current_module_version, patched_module_version)
        data = yaml.load(yaml_doc)
        with open(yaml_path, 'w') as fp:
            yaml.dump(data, fp)
    else:
        import ruamel.yaml
        with open(yaml_path, 'r') as ft:
            all_data = ruamel.yaml.safe_load(ft)
            list_name = []
            for i in all_data['target_modules']:
                list_name.append(i['name'])
            if module_name not in list_name:
                all_data['target_modules'].append(
                    {"name": module_name, "current_module_version": current_module_version,
                     "patched_module_version": patched_module_version})
                with open(yaml_path, 'w') as fm:
                    yaml.dump(all_data, fm)


def test(base_path, path):
    if platform.system().lower() == "windows":
        result = path.split(base_path)[1].split('\\')[1]
        folder_path = os.path.join(base_path, result)
    else:
        result = path.split(base_path)[1].split('/')[1]
        folder_path = os.path.join(base_path, result)
    return folder_path


def get_folder_name(path_str):
    if platform.system().lower() == "windows":
        result = path_str.split('\\')
    else:
        result = path_str.split('/')
    return result


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


def get_dir_allfile(file_dir):
    for root, dirs, files in os.walk(file_dir):
        return files


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
        old_yaml_dir = os.path.join(old_ant_uyun_path, get_folder_name(relative_path_result)[0])
        if 'module.yaml' in get_dir_allfile(old_yaml_dir):
            get_path = os.path.join(patch_path, relative_path_result)
            test = dcmp.right.split(new_ant_uyun_path)[1]
            test1 = test.split(relative_path_result)
            if test1[1] == "":
                file_path = get_path
            else:
                file_path = get_path + test1[1]
        else:
            get_path = os.path.join(patch_path, get_folder_name(relative_path_result)[1])
            test = dcmp.right.split(new_ant_uyun_path)[1]
            test1 = test.split(get_folder_name(relative_path_result)[1])
            if test1[1] == "":
                file_path = get_path
            else:
                file_path = get_path + test1[1]
        create_dir(file_path)
        shutil.copy(whole_path, file_path)
        try:
            deal_result = deal_module_yaml_folder(old_ant_uyun_path, dcmp)
            deal_upatch(patch_path, deal_result[0], deal_result[1], patched_module_version)
        except Exception as e:
            print(e)

    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, old_ant_uyun_path,
                       patch_path, patched_module_version, ignore_maps)


def deal_folder(path):
    if os.path.exists(path):
        for fileList in os.walk(path):
            for name in fileList[2]:
                os.chmod(os.path.join(fileList[0], name), stat.S_IWRITE)
                os.remove(os.path.join(fileList[0], name))
        shutil.rmtree(path)
        create_dir(path)
    else:
        create_dir(path)


def write_patch(path, description):
    if description is not None:
        if len(description) != 0:
            coding = chardet.detect(description)["encoding"]
            content = description.decode(coding).encode('utf8')
            result = content.split(";")
            if len(result) < 3:
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
            else:
                print("error: Does not conform to the description information format")
                return False


def deal_file(old_package_path, new_package_path, new_version, ignore_maps, description, package_name, tar_name):
    """获取处理压缩包"""
    patch_path = os.path.join(os.getcwd(), package_name)
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
        if description is not None:
            if os.path.exists(path):
                result = write_patch(path, description)
                if result is not False:
                    if os.path.exists(path):
                        patch_package(tar_name, patch_path)
                    else:
                        print("The content has not changed")
            else:
                print("The content has not changed")
        else:
            if os.path.exists(path):
                patch_package(tar_name, patch_path)
            else:
                print("The content has not changed")
    except Exception as e:
        print(e)


def get_tar_name(output):
    regex = r"([\w\W]+)-"
    result = re.findall(regex, output)
    result = result[0] + '-patch'
    return result


def main():
    args = docopt(__doc__)
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    output = args['<output>']
    new_version = re_version(output)
    package_name = get_package_name(output)
    tar_name = get_tar_name(output)
    ignore_list = args['<ignore>']
    description = args["--description"]
    ignore_maps = {}
    for ignore in ignore_list:
        if os.path.dirname(ignore) in ignore_maps:
            if os.path.basename(ignore) not in ignore_maps[os.path.dirname(ignore)]:
                ignore_maps[os.path.dirname(ignore)].append(os.path.basename(ignore))
        else:
            ignore_maps[os.path.dirname(ignore)] = [os.path.basename(ignore)]
    deal_file(old_package_path, new_package_path, new_version, ignore_maps, description, package_name, tar_name)


if __name__ == '__main__':
    main()

