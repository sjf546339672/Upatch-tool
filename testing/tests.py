# coding: utf-8
import filecmp
import os
import shutil

import pytest
import re

import time

import yaml

from upatch import (untar, read_yaml, all_file_path, create_dir,
                    re_version, module_yaml_path, patch_package, get_untar_name,
                    deal_upatch)


@pytest.mark.parametrize("path, save_path, result", [
    (r"E:\Uyun-python\Upatch-tool\testing\testuntar\patch.tar.gz",
     r"E:\Uyun-python\Upatch-tool\testing\testuntar",
     r"E:\Uyun-python\Upatch-tool\testing\testuntar\patch",)
])
def test_untar(path, save_path, result):
    """测试解压压缩文件"""
    untar(path, save_path)
    assert os.path.exists(result) is True


@pytest.mark.parametrize("module_yaml_path, version, module_name", [
    (r"E:\Uyun-python\Upatch-tool\new_uyun\platform-ant-dispatcher\module.yaml",
     '2.0.16.41', 'platform-ant-dispatcher')
])
def test_read_yaml(module_yaml_path, version, module_name):
    """测试读取yaml文件获取version"""
    result = read_yaml(module_yaml_path)
    assert result[0] == version
    assert result[1] == module_name


def rm(path):
    shutil.rmtree(path)


@pytest.mark.parametrize("tar_path", [
    r"E:\Uyun-python\Upatch-tool\testing\testallfilepath\file1",
    r"E:\Uyun-python\Upatch-tool\testing\testallfilepath\file2",
    r"E:\Uyun-python\Upatch-tool\testing\testallfilepath\file3"
])
def test_all_file_path(tar_path):
    """测试文件夹中存在tar.gz文件再进行解压"""
    regex = re.compile("[\s\S]*.gz$")
    count = 0
    all_file_path(tar_path)

    for root, folders, files in os.walk(tar_path):
        for file in files:
            file_path = os.path.join(root, file)
            if regex.findall(file_path):
                count += 1
    assert count == 0


@pytest.mark.parametrize("path", [
    r"E:\Uyun-python\Upatch-tool\testing\testcreatedir\test\test\install",
    r"E:\Uyun-python\Upatch-tool\testing\testcreatedir\test\test\test1",
])
def test_create_dir(path):
    """测试递归创建目录"""
    create_dir(path)
    result = os.path.exists(path)
    assert result is True


@pytest.mark.parametrize("str_version, result", [
    ("PSBC-Platform-Ant-lss-V2.0.R16.45-patch.tar.gz", '2.0.16.45')
])
def test_re_version(str_version, result):
    """测试正则匹配version字段"""
    get_result = re_version(str_version)
    assert get_result == result


@pytest.mark.parametrize("base_path, path", [
    (r"E:\Uyun-python\Upatch-tool\testing\testmodule_yaml_path",
     r"E:\Uyun-python\Upatch-tool\testing\testmodule_yaml_path\platform-ant-lvs\keepalived")
])
def test_module_yaml_path(base_path, path):
    result_path = module_yaml_path(base_path, path)
    filename_list = os.listdir(result_path)
    assert 'module.yaml' in filename_list


@pytest.mark.parametrize("output_filename, source_dir", [
    ("test_file2", r"E:\Uyun-python\Upatch-tool\testing\testpatchpackage\file2"),
    ("test_file3", r"E:\Uyun-python\Upatch-tool\testing\testpatchpackage\files3")
])
def test_patch_package(output_filename, source_dir):
    """测试对文件夹进行打包"""
    result = patch_package(output_filename, source_dir)
    assert result is True


@pytest.mark.parametrize("old_list, new_list, result", [
    (["config_util", "crypt", "enable_port"],
     ["config_util", "crypt", "enable_port", "getopt"], "getopt"),
    (["module", "set-env", "uninstall"],
     ["module", "set-env", "uninstall", "util"], "util")
])
def test_get_untar_name(old_list, new_list, result):
    """测试获取解压之后的文件名"""
    file_name = get_untar_name(old_list, new_list)
    assert file_name == result


@pytest.mark.parametrize("patch_path, module_name, current_module_version, patched_module_version", [
    (r"E:\Uyun-python\Upatch-tool\testing\testdealupatch", "platform-ant-lxl", '2.0.3.12', "2.0.5.21")
])
def test_deal_upatch(patch_path, module_name, current_module_version, patched_module_version):
    """测试向patch.yaml文件中添加数据"""
    deal_upatch(patch_path, module_name, current_module_version, patched_module_version)
    f = open(os.path.join(patch_path, "patch.yaml"), 'r')
    yaml_context = f.read()
    res = yaml.load(yaml_context)
    assert res["target_modules"][0]["patched_module_version"] == patched_module_version
    assert res["target_modules"][0]["a-name"] == module_name
    assert res["target_modules"][0]["current_module_version"] == current_module_version


# @pytest.mark.parametrize("dcmp, new_ant_uyun_path, old_ant_uyun_path, patch_path, patched_module_version, ignore_maps", [
#     (filecmp.dircmp(), , , )
# ])
# def test_deal_diff_file():
#     """测试旧包文件和新包文件进行比较"""






