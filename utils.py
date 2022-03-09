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



