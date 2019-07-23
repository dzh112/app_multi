# -*- coding: utf-8 -*-
import os
import socket
import subprocess
from appium import webdriver
import yaml

__author__ = "无声"

import time
from multiprocessing import Process, Value
from core.MultiAdb import MultiAdb as Madb
from core import RunTestCase
import traceback

_print = print
with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


def print(*args, **kwargs):
    _print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)





def main():
    # 默认去config.ini里读取期望参与测试的设备，若为空，则选择当前连接的所有状态为“device”的设备
    devices_List = Madb().get_devicesList()
    if devices_List[0] == "":
        devices_List = Madb().getdevices()
    print("最终的devicesList=", devices_List)
    # 读取是否需要同步性能测试的配置。
    # need_performance = Madb().get_needperformance()
    print("测试开始")
    print("启动appium")

    time.sleep(5)
    if devices_List:
        try:
            print("启动进程池")
            devices_List = devices_List.split(",")
            list1 = []
            # 根据设备列表去循环创建进程，对每个进程调用下面的enter_processing/enter_enter_performance方法。
            for i in range(len(devices_List)):
                # start会被传递到2个进程函数里，作为区分最终产物html和excel的标志

                start = time.localtime()
                madb = Madb(devices_List[i])
                # 进程通信变量flag，默认为0，完成测试时修改为1。
                flag = Value('i', 0)
                p2 = Process(target=enter_processing, args=(i, madb, flag, start))
                list1.append(p2)
            for p in list1:
                p.start()
            for p in list1:
                p.join()
            print("进程回收完毕")

            print("测试结束")
        except Exception as e:
            print("发生未知错误" + traceback.format_exc())
    else:
        print("未找到设备，测试结束")


def enter_processing(processNo, madb, flag, start):
    devices = madb.get_mdevice()
    print("进入{}进程,devicename={}".format(processNo, devices))

    try:
        # 调用airtest的各个方法连接设备
        isconnect = "Pass"
        print("设备{}连接成功".format(devices))
        if isconnect == "Pass":
            try:
                print("设备{}开始安装apk".format(devices))
                # 尝试推送apk到设备上
                install_Result = madb.AppInstall()
                if install_Result:
                    print("{}确定安装成功".format(devices))
            except Exception as e:
                print("{}安装失败，installResult={}".format(devices, install_Result) + traceback.format_exc())
            # try:
            #     time.sleep(madb.get_timeoustartspp())
            #     # 尝试启动应用
            #     app_start(devices)
            # except Exception as e:
            #     print("运行失败" + traceback.format_exc())
            # time.sleep(madb.get_timeoutaction())
            # 应用启动成功则开始运行用例
            RunTestCase.RunTestCase(madb, start)
            # print(start)
            print("{}完成测试".format(devices))
        else:
            print("设备{}连接失败".format(devices))
    except Exception as e:
        print("连接设备{}失败".format(devices) + traceback.format_exc())
    # 无论结果如何，将flag置为1，通知Performance停止记录。
    flag.value = 1








