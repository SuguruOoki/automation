#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
import os
import sys
import glob

root_folder = os.getcwd()

#  フォルダ内のファイルを全て表示する関数
def fild_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)


for file in fild_all_files(root_folder):
    root, ext = os.path.splitext(file)

    if ext == '.bz2':
        # print(os.path.basename(file))
        print(file)
        f = bz2.BZ2File(file).read()
        print(f)
        f.close()
