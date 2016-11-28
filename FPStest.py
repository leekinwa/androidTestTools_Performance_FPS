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

# FPS计算（dumpsys gfxinfo）;
def FPS_count():
    processName = getprocess(seek)
    # 获取gfxinfo的打印值, 如包名为;
    if 'StatusBar' in processName:
        gfxinfo = os.popen( 'adb shell dumpsys gfxinfo com.android.systemui').readlines()
    else:
        gfxinfo = os.popen( 'adb shell dumpsys gfxinfo ' + processName ).readlines()
    # 每帧耗时计算;
    frameList = []
    for gfxinfo_str in gfxinfo:
        frame_1st_split = re.findall( r'\d*\W\d\d[\t\r]', gfxinfo_str )
        if len(frame_1st_split) > 1:
            frame_1st = []
            for i in frame_1st_split:
                frame_1st.append( float(i.replace( r'\t', '').replace( r'\r', '')) )
            frameList.append(sum(frame_1st))
    if len(frameList) > 2:
        # 通过比例计算FPS
        jank_count = 0
        vsync_overtime = 0
        frame_count = len(frameList)
        if frame_count != 0:
            for frame_time in frameList:
                    if frame_time > 16.67:
                        jank_count += 1
                        if frame_time % 16.67 == 0:
                            vsync_overtime += int(frame_time / 16.67) - 1
                        else:
                            vsync_overtime += int(frame_time / 16.67)
            fps = round(frame_count * 60.0 / (frame_count + vsync_overtime), 2)
            return fps, jank_count, vsync_overtime, frame_count
            # print fps
            # print 'jank: ' + str(jank_count)
            # print '垂直同步超时次数: ' + str(vsync_overtime)
            # print '总帧数: ' + str(frame_count)
    elif len(frameList) == 0:
        print u'无法获取帧率数据, 请确保测试设备亮屏并且“开发者选项-GPU呈现模式分析”为打开状态, 脚本退出。'
        exit()

def monkeyRun(operator, runCount):
    if operator == 'UD' or operator == 'ud':
        monkeyRun = subprocess.Popen('adb shell monkey -f /sdcard/monkeyTest_UD.txt ' + str(runCount), shell=True)
    elif operator == 'DU' or operator == 'du':
        monkeyRun = subprocess.Popen('adb shell monkey -f /sdcard/monkeyTest_DU.txt ' + str(runCount), shell=True)
    else:
        monkeyRun = subprocess.Popen('adb shell monkey -f /sdcard/monkeyTest_LR.txt ' + str(runCount), shell=True)
    time.sleep(1)
    fpsList = []
    returncode = monkeyRun.poll()
    while returncode is None:
        FPS_count()
        time.sleep(1)
        fps, jank, vsync, frame_all = FPS_count()
        fpsList.append(fps)
        print u'FPS值: ', fps
        print u'掉帧数: ', jank
        print u'垂直同步区间数: ', vsync
        print u'总帧数: ', frame_all
        print '-------------------------------'
        returncode = monkeyRun.poll()
    fps_avg = round(sum(fpsList) / len(fpsList), 2)
    print u'平均FPS值: ', fps_avg

def main():
    usage = 'FPStest.py [-o <LR, UD, DU>][-c <count>]'
    # 参数解析;
    parser = OptionParser(usage)
    # -o, operateType, 操作类型;
    parser.add_option('-o', dest = 'operateType', help = u'操作类型, LR左右滑动, UD上下滑动, DU下上滑动;')
    # -c, count, 操作次数, 默认30次;
    parser.add_option('-c', dest = 'count', default = '30', help = u'操作次数, 默认30次;')
    (options, args) = parser.parse_args()
    operateType = options.operateType
    count = options.count

    if operateType == 'LR' or operateType == 'lr' or operateType == 'DU' or operateType == 'du' or operateType == 'UD' or operateType == 'ud':
        # print u'操作类型: ', operateType
        # print u'操作次数: ', count
        monkeyRun(operateType, count)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()