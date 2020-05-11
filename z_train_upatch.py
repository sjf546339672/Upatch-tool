# coding: utf-8
"""
Usage:
  upatch.py <old_package_path> <new_package_path> -o <output>  [-i <ignore> <ignore>]
  upatch.py (-h | --help)
  upatch.py (-v | --version)

Options:
  -h, --help    显示帮助信息
  -i, --ignore  忽略目录或文件（可选，忽略的目录或文件不会放入补丁包中）
"""
import filecmp
import tarfile
import os
import re
import shutil
import datetime
import yaml
import time
from docopt import docopt

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
    fp = open(module_yaml_path, 'r', encoding="utf-8")
    result = fp.read()
    dict_yaml = yaml.load(result)
    version = dict_yaml['version']
    module_name = dict_yaml['name']
    return version, module_name


def search_module_yaml(root, target):
    """获取module.yaml文件的绝对路径"""
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


def all_file_path(path):
    """解压后所有文件的路径"""
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


def re_version(filename):
    """正则匹配version字段"""
    pattern = r'\d+'
    result = re.findall(pattern, filename)
    new_version = '.'.join(result)
    return new_version


def deal_diff_file(dcmp, new_ant_uyun_path, patch_path, patched_module_version):
    """旧包文件和新包文件进行比较"""
    for i in dcmp.right_list:
        if i not in dcmp.left_list:
            whole_path = os.path.join(os.path.abspath(dcmp.right), i)
            file_path = dcmp.right.split(new_ant_uyun_path)[1]
            splice_path = patch_path + file_path
            create_dir(splice_path)
            shutil.copy(whole_path, splice_path)

            old_module_yaml_path = search_module_yaml(dcmp.left, "module.yaml")
            current_module_version = read_yaml(old_module_yaml_path)[0]
            new_module_yaml_path = search_module_yaml(dcmp.right, "module.yaml")
            module_name = read_yaml(new_module_yaml_path)[1]
            deal_upatch(patch_path, module_name, current_module_version,
                        patched_module_version)

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
            deal_upatch(patch_path, module_name, current_module_version,
                        patched_module_version)

    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, patch_path, patched_module_version)


def deal_upatch(patch_path, module_name, current_module_version, patched_module_version):
    """向patch.yaml文件中添加数据"""
    yaml_path = os.path.join(patch_path, 'patch.yaml')
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    if not os.path.exists(yaml_path):
        fd = open(yaml_path, mode="w", encoding="utf-8")
        fd.close()
    fp = open(yaml_path, encoding='utf-8')
    yarn_content = fp.read()
    res = yaml.load(yarn_content)
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
        fn = open(yaml_path, 'w', encoding='utf-8')
        if not module_name in list1:
            fn = open(yaml_path, 'w', encoding='utf-8')
            res['release_time'] = datetime.date(year, month, day)
            res['target_modules'].append(
                {'a-name': module_name,
                 'current_module_version': current_module_version,
                 'patched_module_version': patched_module_version
                 }
            )
        yaml.dump(res, fn)
    fp.close()


def deal_ignore(source_dir, ignore_list):
    for root, folders, files in os.walk(source_dir):
        for file in files:
            for i in ignore_list:
                if i in os.path.join(root, file):
                    os.remove(os.path.join(root, file))
        for folder in folders:
            for i in ignore_list:
                if i in os.path.join(root, folder):
                    shutil.rmtree(os.path.join(root, folder))


def patch_package(output_filename, source_dir):
    try:
        with tarfile.open(output_filename + '.tar.gz', "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        shutil.rmtree(source_dir)
        return True
    except Exception as e:
        print(e)
        return False


def deal_file(old_package_path, new_package_path, new_version, ignore_list):
    patch_path = os.path.join(os.getcwd(), 'patch')
    patch_basename = os.path.basename(patch_path)
    if not os.path.isdir(patch_path):
        os.mkdir(patch_path)

    try:
        untar(old_package_path, os.getcwd())
        old_ant_uyun_path = os.path.join(os.getcwd(), 'old_uyun')
        all_file_path(old_ant_uyun_path)

        untar(new_package_path, os.getcwd())
        new_ant_uyun_path = os.path.join(os.getcwd(), 'new_uyun')
        all_file_path(new_ant_uyun_path)

        dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)
        deal_diff_file(dcmp, new_ant_uyun_path, patch_path, new_version)

        deal_ignore(patch_path, ignore_list)
        patch_package(patch_basename, patch_path)
    except Exception as e:
        pass


def main():
    args = docopt(__doc__)
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    output = args['<output>']
    new_version = re_version(output)
    ignore_list = args['<ignore>']
    deal_file(old_package_path, new_package_path, new_version, ignore_list)


if __name__ == '__main__':
    main()


