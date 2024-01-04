#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: adb commands for workspace
# @date:   2023.05.10 14:40:50

import os
import sys
import time

from utils.utils_cmn import CmnUtils
from utils.utils_cmn import CmnProcess
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_file import FileUtils
from utils.utils_adb import AdbUtils

ImportUtils.initEnv()

# --------------------------------------------------------------------------------------------------------------------------
def doDumpUi(path, all):
    LoggerUtils.println('dump ui')
    src = '/sdcard/ui.xml'
    ret, err = CmnUtils.doCmdEx('adb shell uiautomator dump ' + src)
    if CmnUtils.isEmpty(ret) or ret.find('xml') <= 0:
        LoggerUtils.error('Error: fail dump ui, ' + ret + ', ' + err)
        return
    outFile = path + '/ui.xml'
    AdbUtils.pull(src, outFile)
    if not all: LoggerUtils.println('>>> ' + outFile)


def doDumpLogger(path, all):
    LoggerUtils.println('dump log')

    def doDumpLoggerImpl(outFile):
        CmnUtils.doCmd2File('adb logcat -v threadtime', outFile)

    outFile = path + '/log.txt'
    proc = CmnProcess(doDumpLoggerImpl)
    proc.start(outFile)
    LoggerUtils.println('Wait for 3 seconds ...')
    time.sleep(3)
    proc.terminate()
    if not all: LoggerUtils.println('>>> ' + outFile)

def doDumpScreenShot(path, all):
    LoggerUtils.println('dump screenshot')
    CmnUtils.doCmdEx('adb shell screencap -p /sdcard/screenshot.png')
    outFile = path + '/screenshot.png'
    AdbUtils.pull('/sdcard/screenshot.png', outFile)
    if not all: LoggerUtils.println('>>> ' + outFile)

def doDumpProperty(path, all):
    LoggerUtils.println('dump property')
    CmnUtils.doCmd2File('adb shell getprop', path + '/property.txt')
    if not all: LoggerUtils.println('>>> ' + path + '/property.txt')

def doDumpApps(path, all):
    LoggerUtils.println('dump app list')
    CmnUtils.doCmd2File('adb shell pm list packages -e', path + '/app-enabled.txt')
    if not all: LoggerUtils.println('>>> ' + path + '/app-enabled.txt')

    CmnUtils.doCmd2File('adb shell pm list packages -d', path + '/app-disabled.txt')
    if not all: LoggerUtils.println('>>> ' + path + '/app-disabled.txt')

    CmnUtils.doCmd2File('adb shell pm list packages -3', path + '/app-third.txt')
    if not all: LoggerUtils.println('>>> ' + path + '/app-third.txt')

    CmnUtils.doCmd2File('adb shell pm list packages -s', path + '/app-system.txt')
    if not all: LoggerUtils.println('>>> ' + path + '/app-system.txt')

def doDumpRuntime(path, all):
    LoggerUtils.println('dump anr')
    outFile = path + '/anr.txt'
    CmnUtils.doCmd2File('adb pull /data/anr', outFile)
    if not all: LoggerUtils.println('>>> ' + outFile)

    LoggerUtils.println('dump ps')
    outFile = path + '/ps.txt'
    CmnUtils.doCmd2File('adb shell ps', path + '/ps.txt')
    if not all: LoggerUtils.println('>>> ' + outFile)


def doDumpSys(path):
    os.makedirs(path)
    services = CmnUtils.doCmd('adb shell dumpsys -l')
    if not CmnUtils.isEmpty(services):
        items = services.split('\n')
        for item in items:
            item = item.strip()
            if CmnUtils.isEmpty(item) or 0 < item.find('/'): continue
            LoggerUtils.println('dump ' + item)
            CmnUtils.doCmd2File('adb shell dumpsys ' + item, path + os.sep + item + '.txt')


def doDumpEnv(path):
    os.makedirs(path)
    LoggerUtils.println('dump net')
    CmnUtils.doCmd2File('adb shell netcfg', path + '/netcfg.txt')

    LoggerUtils.println('dump property')
    CmnUtils.doCmd2File('adb shell getprop', path + '/property.txt')

    LoggerUtils.println('dump service')
    CmnUtils.doCmd2File('adb shell service list', path + '/service.txt')

class ADBDumper:

    def __init__(self, p):
        self.path = p

    def collect(self, _mode):
        outPath = self.path + os.sep + FileUtils.getTempTimeName('dump_')
        try:
            os.makedirs(outPath)
            if CmnUtils.isEmpty(_mode):
                doDumpUi(outPath, True)
                doDumpRuntime(outPath, True)
                doDumpEnv(outPath + os.sep + 'info')
                doDumpSys(outPath + os.sep + 'sys')
                doDumpLogger(outPath, True)
                doDumpScreenShot(outPath, True)
                doDumpApps(outPath, True)
            elif 'ui' == _mode:
                doDumpUi(outPath, False)
            elif 'sys' == _mode:
                doDumpSys(outPath + os.sep + 'sys')
            elif 'log' == _mode:
                doDumpLogger(outPath, False)
            elif 'shot' == _mode:
                doDumpScreenShot(outPath, False)
            elif 'prop' == _mode:
                doDumpProperty(outPath)
            elif 'app' == _mode:
                doDumpApps(outPath, False)
            else:
                assert 0, 'Unsupported mode: ' + _mode
            LoggerUtils.println('>>> ' + outPath)
        except Exception as e:
            LoggerUtils.println(e)
