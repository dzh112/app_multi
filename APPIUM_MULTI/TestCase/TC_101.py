# -*- coding: utf-8 -*-

from appium import webdriver

import yaml
import unittest
import time

from appium_multi import start_appium_action
from devices_multi import get_port, appium_desired

__author__ = "无声"

_print = print


def print(*args, **kwargs):
    _print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)


def Main(devices):
    print("{}进入unittest".format(devices))

    class TC101(unittest.TestCase):
        u'''测试用例101的集合'''

        @classmethod
        def setUpClass(cls):
            u''' 这里放需要在所有用例执行前执行的部分'''
            # host = '127.0.0.1'
            # port = get_port(devices)
            # start_appium_action(host, port)
            # time.sleep(5)
            pass

        def setUp(self):
            u'''这里放需要在每条用例前执行的部分'''

            pass

        def test_00_of_101(self):
            u'''打开excel03文档'''
            # 每个函数里分别实例poco，否则容易出现pocoserver无限重启的情况
            port = get_port(devices)
            appium_desired(devices, port)

        # def test_02_of_101(self):
        #     u'''用例test_02_of_101的操作步骤'''
        #     # 每个函数里分别实例poco，否则容易出现pocoserver无限重启的情况
        #     poco = UnityPoco()
        #     time.sleep(5)
        #     print("我是TC102的test_02_of_101方法")
        #     Screencap.GetScreen(time.time(), devices, "test_02_of_101的描述")
        #     t = 1
        #     self.assertEquals(2, t)

        def tearDown(self):
            u'''这里放需要在每条用例后执行的部分'''
            """断言截图"""
            pass

        @classmethod
        def tearDownClass(cls):
            u'''这里放需要在所有用例后执行的部分'''
            pass

        # def list2reason(self, exc_list):
        #     if exc_list and exc_list[-1][0] is self:
        #         return exc_list[-1][1]
        #
        # def save_screenshots(self):  # 截图
        #
        #     screenpath = os.path.join(reportpath, "Screen")
        #     Screencap.GetScreen(devices, screenpath, str(self))

    srcSuite = unittest.makeSuite(TC101)
    return srcSuite
