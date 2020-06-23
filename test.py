# coding: utf-8
import os
import shutil
import tarfile

output_filename = "aaa"
source_dir = "E:\Uyun-python\Upatch-tool\platform-ant"

from subprocess import Popen
import subprocess
import os
get_cwd = os.getcwd()
#
# pg = Popen("", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
# buff, buffErr = pg.communicate()
# print(buff.decode("GBK"))
# print(buffErr)
shutil.move("E:\Uyun-python\Upatch-tool\platform-ant\patch.yaml", get_cwd)
