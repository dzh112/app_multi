# -*- coding: utf-8 -*-
__author__ = "无声"
import configparser
import os

con = configparser.ConfigParser()


# 解析config文件并将其结果转成一个list，对单个的value，到时候可以用[0]来取到。
def getValue(path, key):
    con.read(path,encoding="utf-8")
    result = con.get("config", key)
    list = result.split(",")
    return list

    # 基本同上，读取TestCaseforDevice 节点下的键值


def getTestCase(caselist):
    if caselist != "":
        list = caselist.split(",")
        return list
    else:
        return []

    # 重新写回配置文件



