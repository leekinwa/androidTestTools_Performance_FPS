# -*- coding: utf-8 -*-
import os, platform, re, time, subprocess, FPS_script
from optparse import OptionParser

# 判断手机内是否有执行脚本, 如无则生成脚本;
scriptFiles_exist = os.popen('adb shell ls /sdcard/').read()
if 'monkeyTest_UD.txt' not in scriptFiles_exist:
    FPS_script.main()

# 判断系统平台;
if platform.system() == 'Windows':
    seek = 'findstr'
else:
    seek = 'grep'

# 获取包名函数;
def getprocess(seek):
    getWindow = os.popen('adb shell dumpsys window | ' + seek + ' mCurrentFocus').readline().split()[-1]
    processName = getWindow.split(r'/')[0]
    # print processName
    return processName

def gfx_switch_state():
    get_gfxSwitch = os.popen('adb shell getprop debug.hwui.profile').read()
    if 'true' in get_gfxSwitch or 'visual_bars' in get_gfxSwitch:
        pass
    else:
        print u'无法获取帧率数据, 请打开“开发者选项-GPU呈现模式分析”开关, 脚本退出。'
        exit()

def get_vsync_time():
    vsyncTime = 0
    get_vsyncTime = os.popen('adb shell dumpsys SurfaceFlinger | grep refresh=').read().split(',')
    for line in get_vsyncTime:
        if 'refresh' in line:
            vsyncTime = round(float(line.split('=')[1]) / 1000000, 2)
    return vsyncTime

# FPS计算（dumpsys gfxinfo）;
def FPS_count(vsyncTime):
    processName = getprocess(seek)
    # 获取gfxinfo的打印值, 如包名为;
    if 'StatusBar' in processName:
        gfxinfo_command = 'adb shell dumpsys gfxinfo com.android.systemui'
    else:
        gfxinfo_command = 'adb shell dumpsys gfxinfo %s' %processName
    os.popen(gfxinfo_command)
    time.sleep(1)
    gfxinfo = os.popen(gfxinfo_command).readlines()
    # 每帧耗时计算;
    frameList = []
    for gfxinfo_str in gfxinfo:
        frame_1st_split = re.findall( r'\d*\W\d\d[\t\r]', gfxinfo_str )
        if len(frame_1st_split) > 1:
            frame_1st = []
            for i in frame_1st_split:
                frame_1st.append( float(i.replace( r'\t', '').replace( r'\r', '')) )
            frameList.append(sum(frame_1st))
    if len(frameList) != 0:
        # 通过比例计算FPS
        jank_count = 0
        vsync_overtime = 0
        frame_count = len(frameList)
        for frame_time in frameList:
                if frame_time > vsyncTime:
                    jank_count += 1
                    if frame_time % vsyncTime == 0:
                        vsync_overtime += int(frame_time / vsyncTime) - 1
                    else:
                        vsync_overtime += int(frame_time / vsyncTime)
        fps = round(frame_count * 60.0 / (frame_count + vsync_overtime), 2)
        return fps, jank_count, vsync_overtime, frame_count

def monkey_command():
    monkeyCommand = ''
    usage = 'FPStest.py [-o <LR, UD, DU>][-c <count>]'
    # 参数解析;
    parser = OptionParser(usage)
    parser.add_option('-o', dest = 'operateType', help = u'操作类型, LR左右滑动, UD上下滑动, DU下上滑动;')
    parser.add_option('-c', dest = 'count', default = '30', help = u'操作次数, 默认30次;')
    (options, args) = parser.parse_args()
    operateType = options.operateType
    count = options.count
    if operateType == 'UD' or operateType == 'ud':
        monkeyCommand = 'adb shell monkey -f /sdcard/monkeyTest_UD.txt %s' %count
    elif operateType == 'DU' or operateType == 'du':
        monkeyCommand = 'adb shell monkey -f /sdcard/monkeyTest_DU.txt %s' %count
    elif operateType == 'LR' or operateType == 'lr':
        monkeyCommand = 'adb shell monkey -f /sdcard/monkeyTest_LR.txt %s' %count
    else:
        parser.print_help()
        exit()
    return monkeyCommand

def monkey_run():
    monkeyCommand = monkey_command()
    gfx_switch_state()
    vsyncTime = get_vsync_time()
    monkeyRun = subprocess.Popen(monkeyCommand, shell = True)
    time.sleep(1)
    fps_list = []
    jank_list = []
    frame_all = []
    returncode = monkeyRun.poll()
    while returncode is None:
        fps, jank, vsync, frame_count = FPS_count(vsyncTime)
        fps_list.append(fps)
        jank_list.append(jank)
        frame_all.append(frame_count)
        print u'FPS值:', fps
        print u'掉帧数:', jank
        print u'垂直同步超时区间:', vsync
        print u'总帧数:', frame_count
        print '-------------------------------'
        returncode = monkeyRun.poll()
    fps_avg = round(sum(fps_list) / len(fps_list), 2)
    jank_percent = round(float(sum(jank_list)) / sum(frame_all) * 100, 2)
    print u'平均FPS值:', fps_avg
    print u'掉帧率: %s%%' %jank_percent

def main():
    monkey_run()

if __name__ == '__main__':
    main()