# coding: utf-8
"""
Usage:
  upatch.py <old_package_path> <new_package_path> -o <output>  [-i <ignore> <ignore>]
  upatch.py (-h | --help)
  upatch.py (-v | --version)
Options:
  -h, --help             显示帮助信息
  -i, --ignore  忽略目录或文件（可选，忽略的目录或文件不会放入补丁包中）
"""
import filecmp
import tarfile
import os
import re
import shutil
import datetime
import platform
import yaml
import time
from docopt import docopt

regex = re.compile("[\s\S]*.gz$")
host_platform = platform.system().lower()


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


def re_module_yaml_path(base_path, path):
    """获取module.yaml文件夹"""
    split_path = os.path.split(path)
    if base_path == split_path[0]:
        old_path = path
    else:
        data = path.split(base_path)
        data_list = data[1].split('/')
        old_path = os.path.join(base_path, data_list[1])
    return old_path


def deal_module_yaml_folder(old_ant_uyun_path, dcmp):
    """获取模块名和旧包yaml中的版本号"""
    module_yaml_folder = re_module_yaml_path(old_ant_uyun_path, os.path.abspath(dcmp.left))
    old_module_yaml_path = os.path.join(module_yaml_folder, 'module.yaml')
    current_module_version = read_yaml(old_module_yaml_path)[0]
    module_name = read_yaml(old_module_yaml_path)[1]
    return module_name, current_module_version


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
        if module_name not in list1:
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


def get_all_files(package_path):
    list_files_one = os.listdir(os.getcwd())
    untar(package_path, os.getcwd())
    list_files_two = os.listdir(os.getcwd())
    file_name = get_untar_name(list_files_one, list_files_two)
    ant_uyun_path = os.path.join(os.getcwd(), file_name)
    all_file_path(ant_uyun_path)
    return ant_uyun_path


def deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path,
                   patched_module_version, ignore_maps):
    """旧包文件和新包文件进行比较"""
    relative_path = dcmp.right.split(new_ant_uyun_path)
    relative_path_result = relative_path[1][1:]
    if relative_path_result in ignore_maps:
        dcmp.ignore = ignore_maps[relative_path_result]

    filename_list = []
    filename_list += dcmp.diff_files
    filename_list += dcmp.right_only
    if filename_list != []:
        for i in filename_list:
            whole_path = os.path.join(dcmp.right, i)
            file_path = dcmp.right.split(new_ant_uyun_path)[1][1:]
            splice_path = os.path.join(patch_path, file_path)
            create_dir(splice_path)
            shutil.copy(whole_path, splice_path)
            try:
                deal_result = deal_module_yaml_folder(old_ant_uyun_path, dcmp)
                deal_upatch(patch_path, deal_result[0], deal_result[1], patched_module_version)
            except Exception as e:
                print(e)

    for sub_dcmp in dcmp.subdirs.values():
        deal_diff_file(sub_dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path, patched_module_version, ignore_maps)


def deal_file(old_package_path, new_package_path, new_version, ignore_maps):
    """获取处理压缩包"""
    patch_path = os.path.join(os.getcwd(), 'patch')
    if not os.path.exists(patch_path):
        os.mkdir(patch_path)
    else:
        shutil.rmtree(patch_path)
        os.mkdir(patch_path)

    try:
        old_ant_uyun_path = get_all_files(old_package_path)
        new_ant_uyun_path = get_all_files(new_package_path)
        dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)
        deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path,
                       patch_path, new_version, ignore_maps)
        patch_package('patch', patch_path)
    except Exception as e:
        pass

    # try:
    #     untar(old_package_path, os.getcwd())
    #     old_ant_uyun_path = os.path.join(os.getcwd(), 'old_uyun')
    #     all_file_path(old_ant_uyun_path)
    #
    #     untar(new_package_path, os.getcwd())
    #     new_ant_uyun_path = os.path.join(os.getcwd(), 'new_uyun')
    #     all_file_path(new_ant_uyun_path)
    #
    #     dcmp = filecmp.dircmp(old_ant_uyun_path, new_ant_uyun_path)
    #     deal_diff_file(dcmp, new_ant_uyun_path, old_ant_uyun_path,
    #                    patch_path, new_version, ignore_maps)
    #     patch_package('patch', patch_path)
    # except Exception as e:
    #     pass


def main():
    args = docopt(__doc__)
    old_package_path = args['<old_package_path>']
    new_package_path = args['<new_package_path>']
    output = args['<output>']
    new_version = re_version(output)
    ignore_list = args['<ignore>']
    ignore_maps = {}
    for ignore in ignore_list:
        if os.path.dirname(ignore) in ignore_maps:
            if os.path.basename(ignore) not in ignore_maps[os.path.dirname(ignore)]:
                ignore_maps[os.path.dirname(ignore)].append(os.path.basename(ignore))
        else:
            ignore_maps[os.path.dirname(ignore)] = [os.path.basename(ignore)]
    deal_file(old_package_path, new_package_path, new_version, ignore_maps)


if __name__ == '__main__':
    main()

