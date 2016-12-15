# -*- coding: utf-8 -*-

import os, time


def wait_for_device():
    device_exsit = ''
    reTry = 0
    while reTry < 10:
        getDevices_command = 'adb get-state'
        getDevices = os.popen(getDevices_command).readline()
        if 'device' in getDevices:
            device_exsit = True
            break
        else:
            os.popen('adb -s kill-server')
            time.sleep(2)
            os.popen('adb -s start-server')
            device_exsit = False
            reTry += 1
    if device_exsit == False:
        print u'未识别到手机，请查看手机是否连接成功。'
        exit()

def main():
    wait_for_device()
    fileHead =\
    '''type = user
    count = 10
    speed = 1.0
    start data >>

    '''
    # 获取测试设备屏幕分辨率;
    wm = os.popen('adb shell wm size').read().split()[2].split('x')
    x = int(wm[0])
    y = int(wm[1])

    # 事件间不加延时;
    monkey_DU = 'Drag(' + str(x*0.5) + ', ' + str(y*0.3) + ', ' + str(x*0.5) + ', ' + str(y*0.8) + ',' + str(int(y*0.8 - y*0.2)/5) + ')\n'
    monkey_UD = 'Drag(' + str(x*0.5) + ', ' + str(y*0.8) + ', ' + str(x*0.5) + ', ' + str(y*0.3) + ',' + str(int(y*0.8 - y*0.2)/5) + ')\n'
    monkey_LR = 'Drag(' + str(x*0.2) + ', ' + str(y*0.5) + ', ' + str(x*0.8) + ', ' + str(y*0.5) + ',' + str(int(x*0.8 - x*0.2)/5) + ')\n'
    monkey_RL = 'Drag(' + str(x*0.8) + ', ' + str(y*0.5) + ', ' + str(x*0.2) + ', ' + str(y*0.5) + ',' + str(int(x*0.8 - x*0.2)/5) + ')\n'
    # print monkey_DU, monkey_UD

    # 列表超过300元素
    monkeyFile_UD = fileHead + monkey_UD *2 + monkey_DU *2
    monkeyFile_DU = fileHead + monkey_DU *2 + monkey_UD *2
    monkeyFile_LR = fileHead + monkey_RL *2 + monkey_LR *2

    # 生成monkey测试脚本;
    file_object = open('./monkeyTest_UD.txt', 'w')
    file_object.writelines(monkeyFile_UD)
    file_object.close()
    file_object = open('./monkeyTest_DU.txt', 'w')
    file_object.writelines(monkeyFile_DU)
    file_object.close()
    file_object = open('./monkeyTest_LR.txt', 'w')
    file_object.writelines(monkeyFile_LR)
    file_object.close()

    # 把monkey测试脚本push到手机sdcard目录;
    os.popen('adb push ./monkeyTest_UD.txt /sdcard/')
    os.popen('adb push ./monkeyTest_DU.txt /sdcard/')
    os.popen('adb push ./monkeyTest_LR.txt /sdcard/')
    os.remove('./monkeyTest_UD.txt')
    os.remove('./monkeyTest_DU.txt')
    os.remove('./monkeyTest_LR.txt')

if __name__ == '__main__':
    main()