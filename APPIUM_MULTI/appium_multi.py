import os
import socket
import subprocess
from time import sleep
import multiprocessing
import yaml
from time import ctime

with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)


def appium_start_sync():
    '''并发启动appium服务'''
    print('====appium_start_sync=====')

    # 构建appium进程组
    appium_process = []

    # 加载appium进程

    for i in range(len(data['devices_list'].split(","))):
        host = '127.0.0.1'
        port = 4723 + 2 * i

        appium = multiprocessing.Process(target=start_appium_action, args=(host, port))
        appium_process.append(appium)

        # 启动appium服务
    for appium in appium_process:
        appium.start()
    for appium in appium_process:
        appium.join()

    sleep(5)


def start_appium_action(host, port):
    '''检测端口是否被占用，如果没有被占用则启动appium服务'''
    if check_port(host, port):
        appium_start(host, port)
    else:
        print('appium %s start failed!' % port)
        release_port(port)

    return True


def check_port(host, port):
    """检测指定的端口是否被占用"""

    # 创建socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.shutdown(2)
    except OSError as msg:
        print('port %s is available! ' % port)
        print(msg)
        return True
    else:
        print('port %s already be in use !' % port)
        return False


def appium_start(host, port):
    '''启动appium server'''
    bootstrap_port = str(port + 1)
    cmd = 'start /b appium -a ' + host + ' -p ' + str(port) + ' -bp ' + str(bootstrap_port)

    print('%s at %s' % (cmd, ctime()))
    subprocess.Popen(cmd, shell=True, stdout=open('./appium_log/' + str(port) + '.log', 'a'), stderr=subprocess.STDOUT)


def release_port(port):
    """释放指定的端口"""

    # 查找对应端口的pid
    cmd_find = 'netstat -aon | findstr %s' % port
    print(cmd_find)

    # 返回命令执行后的结果
    result = os.popen(cmd_find).read()
    print(result)

    if str(port) and 'LISTENING' in result:
        # 获取端口对应的pid进程
        i = result.index('LISTENING')
        start = i + len('LISTENING') + 7
        end = result.index('\n')
        pid = result[start:end]

        # 关闭被占用端口的pid
        cmd_kill = 'taskkill -f -pid %s' % pid
        print(cmd_kill)
        os.popen(cmd_kill)

    else:
        print('port %s is available !' % port)


if __name__ == '__main__':
    appium_start_sync()
    # for i in range(60):
    #     release_port(i+4720)
