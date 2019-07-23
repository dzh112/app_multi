import time
from core.MultiAdb import MultiAdb as Madb
import yaml
from appium import webdriver

with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


def app_start(device):
    desired_caps = {}
    desired_caps['platformName'] = data['platformName']
    desired_caps['platformVersion'] = data['platformVersion']
    desired_caps['deviceName'] = data['deviceName']
    desired_caps['udid'] = device

    desired_caps['appPackage'] = data['packname']
    desired_caps['appActivity'] = data['activity']
    desired_caps['noReset'] = data['noReset']
    madb = Madb(device)
    print(int(madb.get_nickname()))
    i = 0
    if int(madb.get_nickname()) == 62001:
        i = 0
    elif int(madb.get_nickname()) == 62025:
        i = 1
    elif int(madb.get_nickname()) > 62025:
        i = 2 + (int(madb.get_nickname()) - 62025)
    port = 4723 + 2 * i
    print('appium port:%s start run %s at %s' % (port, device, time.ctime()))
    driver_address = 'http://' + str(data['ip']) + ':' + str(port) + '/wd/hub'
    driver = webdriver.Remote(driver_address, desired_caps)
    driver.implicitly_wait(5)


app_start("127.0.0.1:62001")
