import multiprocessing
from appium import webdriver
import yaml
from time import ctime
import os

with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


def devices_start_sync():
    '''并发启动设备'''
    print('===devices_start_sync===')

    # 定义desired进程组
    desired_process = []

    # 加载desired进程
    for i in range(len(data['devices_list'])):
        port = 4723 + 2 * i
        desired = multiprocessing.Process(target=appium_desired, args=(data['devices_list'][i], port))
        desired_process.append(desired)

    # 并发启动App
    for desired in desired_process:
        desired.start()
    for desired in desired_process:
        desired.join()


def get_port(device):
    madb = 0
    i = 0
    if ":" in device:
        madb = int(device.split(":")[1])

    if madb == 62001:
        i = 0
    elif madb == 62025:
        i = 1
    elif madb > 62025:
        i = 2 + (madb - 62025)
    port = 4723 + 2 * i
    return port


def appium_desired(udid,port):
    desired_caps = {}
    desired_caps['platformName'] = data['platformName']
    desired_caps['platformVersion'] = data['platformVersion']
    desired_caps['deviceName'] = data['deviceName']
    desired_caps['udid'] = udid
    desired_caps['appPackage'] = data['packname']
    desired_caps['appActivity'] = data['activity']
    desired_caps['noReset'] = data['noReset']
    # port = get_port(udid)
    print('appium port:%s start run %s at %s' % (port, udid, ctime()))
    driver = webdriver.Remote('http://127.0.0.1:' + str(port) + '/wd/hub', desired_caps)

    driver.implicitly_wait(5)
    return driver


if __name__ == '__main__':
    devices_start_sync()
