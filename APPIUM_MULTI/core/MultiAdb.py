# -*- coding: utf-8 -*-
import time

import yaml
from airtest.core.android.adb import ADB

__author__ = "无声"

import os, inspect
import sys
import threading
import queue
from core import RunTestCase
from tools import Config
import subprocess

_print = print


def print(*args, **kwargs):
    _print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)


adb = ADB().adb_path
# 同文件内用queue进行线程通信
q = queue.Queue()
with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


class MultiAdb:

    def __init__(self, mdevice=""):
        # 获取当前文件的上层路径
        self._parentPath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())) + os.path.sep + ".")
        # 获取当前项目的根路径
        self._rootPath = os.path.abspath(os.path.dirname(self._parentPath) + os.path.sep + ".")

        self._devicesList = data['devices_list']
        self._packagePath = data['apkpath']
        self._packageName = data['packname']
        self._activity = data['activity']
        self._mdevice = mdevice
        # 处理模拟器端口用的冒号
        if ":" in self._mdevice:
            self._nickName = self._mdevice.split(":")[1]
        else:
            self._nickName = self._mdevice
        self._allTestcase = data['testcase']
        try:
            app_nick = 'app' + self._nickName
            self._testcaseForSelfDevice = Config.getTestCase(data['TestCaseforDevice'][app_nick])
            if self._testcaseForSelfDevice == "":
                self._testcaseForSelfDevice = self._allTestcase
        except Exception:
            self._testcaseForSelfDevice = self._allTestcase

        self._testCasePath = data['testcasepath']
        if self._testCasePath is None:
            self._testCasePath = os.path.join(self._rootPath, "TestCase")
        # self._needPerformance = Config.getValue(self._configPath, "needPerformance")[0]

    # 获取设备列表
    def get_devicesList(self):
        return self._devicesList

    # 获取apk的本地路径
    def get_apkpath(self):
        return self._packagePath

    # 获取包名
    def get_packagename(self):
        return self._packageName

    def get_activity(self):
        return self._activity

    # 获取当前设备id
    def get_mdevice(self):
        return self._mdevice

    # 获取当前设备id的昵称，主要是为了防范模拟器和远程设备带来的冒号问题。windows的文件命名规范里不允许有冒号。
    def get_nickname(self):
        return self._nickName

    # 获取所有的用例名称列表
    def get_alltestcase(self):
        return self._allTestcase

    # 获取针对特定设备的用例列表
    def get_testcaseforselfdevice(self):
        return self._testcaseForSelfDevice

    # 获取测试用例路径，不填是默认根目录TestCase
    def get_TestCasePath(self):
        return self._testCasePath

    # 获取项目的根目录绝对路径
    def get_rootPath(self):
        return self._rootPath

    # 获取是否需要性能测试的开关
    # def get_needperformance(self):
    #     return self._needPerformance

    # 修改当前设备的方法
    def set_mdevice(self, device):
        self._mdevice = device

    # 写回包名、包路径、测试用例路径等等到配置文件

    # def set_packagename(self, packagename):
    #     data['packname'] = packagename
    #
    # def set_packagepath(self, packagepath):
    #     data['apkpath'] = packagepath
    #
    # def set_TestCasePath(self, TestCasepath):
    #     data['testcasepath'] = TestCasepath

    # 本方法用于读取实时的设备连接
    def getdevices(self):
        deviceslist = []
        for devices in os.popen(adb + " devices"):
            if "\t" in devices:
                if devices.find("emulator") < 0:
                    if devices.split("\t")[1] == "device\n":
                        deviceslist.append(devices.split("\t")[0])
                        print("设备{}被添加到deviceslist中".format(devices))
        return deviceslist

    # 安装应用的方法，先判断应用包是否已安装，如已安装则卸载，然后按配置路径去重新安装。
    def AppInstall(self):
        devices = self.get_mdevice()
        apkpath = self.get_apkpath()
        package = self.get_packagename()

        print("设备{}开始进行自动安装".format(devices))
        try:
            if self.isinstalled():
                uninstallcommand = adb + " -s " + str(devices) + " uninstall " + package
                print("正在{}上卸载{},卸载命令为：{}".format(devices, package, uninstallcommand))
                os.popen(uninstallcommand)
            time.sleep(1.0)
            installcommand = adb + " -s " + str(devices) + " install -r " + apkpath
            os.popen(installcommand)
            print("正在{}上安装{},安装命令为：{}".format(devices, package, installcommand))
            time.sleep(15)
            if self.isinstalled():
                print("{}上安装成功，退出AppInstall线程".format(devices))
                # 将线程函数的返回值放入queue
                q.put("Install Success")
                return True
            else:
                print("{}上安装未成功".format(devices))
                q.put("Install Fail")
                return False
        except Exception as e:
            print("{}上安装异常".format(devices))
            print(e)
            q.put("Install Fail")

    # 判断给定设备里是否已经安装了指定apk
    def isinstalled(self):
        devices = self.get_mdevice()
        package = self.get_packagename()
        command = adb + " -s {} shell pm list package".format(devices)
        commandresult = os.popen(command)
        print("设备{}进入isinstalled方法，package={}".format(devices, package))

        for pkg in commandresult:
            # print(pkg)
            if "package:" + package in pkg:
                print("在{}上发现已安装{}".format(devices, package))
                return True
        print("在{}上没找到包{}".format(devices, package))
        return False

    # 判断给定设备的安卓版本号
    def get_androidversion(self):
        command = adb + " -s {} shell getprop ro.build.version.release".format(self.get_mdevice())
        version = os.popen(command).read()[0]
        return int(version)

    # 判断给定设备运行指定apk时的内存占用
    def get_allocated_memory(self):
        command = adb + " -s {} shell dumpsys meminfo {}".format(self.get_mdevice(), self.get_packagename())
        print(command)
        memory = os.popen(command)
        list = []
        for line in memory:
            line = line.strip()
            list = line.split(' ')
            if list[0] == "TOTAL":
                while '' in list:
                    list.remove('')
                allocated_memory = format(int(list[1]) / 1024, ".2f")
                q.put(allocated_memory)
                return allocated_memory
        q.put("N/a")
        return "N/a"

    # 判断给定设备运行时的内存总占用
    def get_totalmemory(self):
        command = adb + " -s {} shell dumpsys meminfo ".format(self.get_mdevice())
        print(command)
        memory = os.popen(command)
        TotalRAM = 0
        for line in memory:
            line = line.strip()
            list = line.split(":")
            if list[0] == "Total RAM":
                if self.get_androidversion() < 7:
                    TotalRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif self.get_androidversion() > 6:
                    TotalRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
                break
        q.put(TotalRAM)
        return TotalRAM

    # 判断给定设备运行时的空闲内存
    def get_freememory(self):
        command = adb + " -s {} shell dumpsys meminfo ".format(self.get_mdevice())
        print(command)
        memory = os.popen(command)
        FreeRAM = 0
        for line in memory:
            line = line.strip()
            list = line.split(":")
            if list[0] == "Free RAM":
                if self.get_androidversion() < 7:
                    FreeRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif self.get_androidversion() > 6:
                    FreeRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
                break
        q.put(FreeRAM)
        return FreeRAM

    # 判断给定设备运行时的总使用内存
    def get_usedmemory(self):
        command = adb + " -s {} shell dumpsys meminfo ".format(self.get_mdevice())
        print(command)
        memory = os.popen(command)
        UsedRAM = 0
        for line in memory:
            line = line.strip()
            list = line.split(":")
            if list[0] == "Used RAM":
                if self.get_androidversion() < 7:
                    UsedRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif self.get_androidversion() > 6:
                    UsedRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
                break
        q.put(UsedRAM)
        return UsedRAM

    # 判断给定设备运行时的Total/Free/Used内存,一次dump，加快获取速度
    def get_memoryinfo(self):
        command = adb + " -s {} shell dumpsys meminfo ".format(self.get_mdevice())
        print(command)
        memory = os.popen(command)
        androidversion = self.get_androidversion()
        for line in memory:
            line = line.strip()
            list = line.split(":")
            if list[0] == "Total RAM":
                if androidversion < 7:
                    TotalRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif androidversion > 6:
                    TotalRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
            elif list[0] == "Free RAM":
                if androidversion < 7:
                    FreeRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif androidversion > 6:
                    FreeRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
            elif list[0] == "Used RAM":
                if androidversion < 7:
                    UsedRAM = format(int(list[1].split(" ")[1]) / 1024, ".2f")
                elif androidversion > 6:
                    UsedRAM = format(int(list[1].split("K")[0].replace(",", "")) / 1024, ".2f")
        q.put(TotalRAM, FreeRAM, UsedRAM)
        return TotalRAM, FreeRAM, UsedRAM

    # 判断给定设备运行时的总CPU占用，对安卓8以上，CPU总数不一定是100%，视手机CPU内核数决定。
    def get_totalcpu(self):
        starttime = time.time()
        command = adb + " -s {} shell top -n 1 ".format(self.get_mdevice())
        print(command)
        commandresult = os.popen(command)
        cputotal = 0
        andversion = self.get_androidversion()
        # print("get_totalcpu",time.time()-starttime)
        maxcpu = ""
        for line in commandresult:
            list = line.strip().split(" ")
            while '' in list:
                list.remove('')
            # print(list)
            if len(list) > 8:
                if andversion < 7:
                    # print(list)
                    if ("%" in list[2] and list[2] != "CPU%"):
                        cpu = int(list[2][:-1])
                        if cpu != 0:
                            cputotal = cputotal + cpu
                        else:
                            break
                elif andversion == 7:
                    # print(list)
                    if ("%" in list[4] and list[4] != "CPU%"):
                        cpu = int(list[4][:-1])
                        if cpu != 0:
                            cputotal = cputotal + cpu
                        else:
                            break
                elif andversion > 7:
                    # print(list)
                    if "%cpu" in list[0]:
                        maxcpu = list[0]
                        # print(list)
                        # print(maxcpu)
                    try:
                        cpu = float(list[8])
                        if cpu != 0:
                            cputotal = cputotal + cpu
                        else:
                            break
                    except:
                        pass
        totalcpu = str(format(cputotal, ".2f")) + "%"
        q.put(totalcpu, maxcpu)
        return totalcpu, maxcpu

    # 判断给定设备运行时的总使用CPU
    def get_allocated_cpu(self):
        start = time.time()
        # 包名过长时，包名会在adbdump里被折叠显示，所以需要提前将包名压缩，取其前11位基本可以保证不被压缩也不被混淆
        packagename = self.get_packagename()[0:11]
        command = adb + " -s {} shell top -n 1 |findstr {} ".format(self.get_mdevice(), packagename)
        print(command)
        subresult = os.popen(command).read()
        version = self.get_androidversion()
        if subresult == "":
            q.put("N/a")
            return "N/a"
        else:
            cpuresult = subresult.split(" ")
            # 去空白项
            while '' in cpuresult:
                cpuresult.remove('')
            # print(self.get_mdevice(),"cpuresult=",cpuresult)
            if version == 6:
                cpu = cpuresult[2]
            elif version == 7:
                cpu = cpuresult[4]
            elif version > 7:
                cpu = cpuresult[8] + "%"
            q.put(cpu)
            return cpu
