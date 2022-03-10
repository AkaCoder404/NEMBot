#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定义几个函数 写文件 通知 返回键 创建目录 创建文件
"""
import os
import platform
import subprocess

from collections import OrderedDict


__all__ = [
    "utf8_data_to_file",
    "notify",
    "uniq",
    "create_file",
]


def utf8_data_to_file(f, data):
    if hasattr(data, "decode"):
        f.write(data.decode("utf-8"))
    else:
        f.write(data)


def mkdir(path):
    try:
        os.mkdir(path)
        return True
    except OSError:
        return False


def create_dir(path):
    if not os.path.exists(path):
        return mkdir(path)
    elif os.path.isdir(path):
        return True
    else:
        os.remove(path)
        return mkdir(path)


def create_file(path, default="\n"):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(default)

