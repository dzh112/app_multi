from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

auto_setup(__file__)
dev1 = connect_device('Android:///127.0.0.1:62001?cap_method=JAVACAP&&ori_method=ADBORI&&touch_method=ADBTOUCH')
poco = AndroidUiautomationPoco(dev1, use_airtest_input=True, screenshot_each_action=False)
clear_app('com.yozo.office')
start_app('com.yozo.office')
while True:
    sleep(0.5)
    while poco(text="允许").exists():
        poco(text="允许").click()
    sleep(0.5)
    while poco(text="始终允许").exists():
        poco(text="始终允许").click()
    sleep(0.5)
    if poco("com.yozo.office:id/rl_1").exists():
        break
while not poco("com.yozo.office:id/ll_usednow").exists():
    poco.swipe([0.8, 0.5], [0, 0.5])
poco("com.yozo.office:id/ll_usednow").wait().click()
