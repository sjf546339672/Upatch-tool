# coding: utf-8
import tarfile
import os
import re
import shutil
import filecmp

old_package_path = r'E:\AllProject\MyProject\Upatch-tool\UYUN-Ant.tar.gz'
new_package_path = r'E:\AllProject\MyProject\Upatch-tool\uyun-ant\UYUN-Ant.tar.gz'


class Upatch(object):

    regex = re.compile("[\s\S]*.gz$")
    list_path = []

    def untar(self, path, save_path):
        """解压压缩文件"""
        try:
            tar = tarfile.open(path)
            tar.extractall(save_path)
            tar_path = os.path.join(save_path, tar.getnames()[0])
            return tar_path
        except Exception as e:
            print(e)

    def all_file_path(self, path):
        for root, folders, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.regex.findall(file_path):
                    current_path = os.path.abspath(os.path.dirname(file_path))
                    path = self.untar(file_path, current_path)
                    self.all_file_path(path)
                    os.remove(file_path)
                else:
                    self.list_path.append(file_path)
            for folder in folders:
                folder_path = os.path.join(root, folder)
                self.all_file_path(folder_path)

    def all_file_path_list(self, package_path, save_path):
        path = self.untar(package_path, save_path)
        self.all_file_path(path)

    def deal_file(self, old_package_path, new_package_path):
        self.all_file_path_list(old_package_path,
                                os.path.abspath(os.path.dirname(old_package_path)))
        self.all_file_path_list(new_package_path,
                                os.path.abspath(os.path.dirname(new_package_path)))

upatch = Upatch()