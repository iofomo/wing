#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: adb commands for workspace
# @date:   2023.05.10 14:40:50

import os
import sys
import time

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_file import FileUtils
from utils.utils_adb import AdbUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
def doTopInfo():
    AdbUtils.printlnDump()


def doPullPackage(projPath, pkg):
    if CmnUtils.isEmpty(pkg):
        LoggerUtils.error('Error: Invalid commands')
        LoggerUtils.println('The command is: "wing -adb pull {package name}"')
        return

    pkgFile = AdbUtils.getApkFile(pkg)
    if CmnUtils.isEmpty(pkgFile):
        LoggerUtils.error('Error: ' + pkg + ' not found')
        return
    outFile = projPath + os.sep + pkg + '.apk'
    if not AdbUtils.pull(pkgFile, outFile):
        LoggerUtils.error('Error: pull ' + pkgFile + ' Failed')
        return
    LoggerUtils.light('from: ' + pkgFile)
    LoggerUtils.light('  to: ' + os.path.basename(outFile))


def doStopApp(projPath, pkg):
    if not CmnUtils.isEmpty(pkg):
        AdbUtils.stop(pkg)
        return


def doClearApp(projPath, pkg):
    if not CmnUtils.isEmpty(pkg):
        AdbUtils.clear(pkg)
        return


def doDumpUi(path):
    LoggerUtils.println('dump ui')
    src = '/sdcard/ui.xml'
    ret, err = CmnUtils.doCmdEx('adb shell uiautomator dump ' + src)
    if CmnUtils.isEmpty(ret) or ret.find('xml') <= 0:
        LoggerUtils.error('Error: fail dump ui, ' + ret + ', ' + err)
        return
    outFile = path + '/ui.xml'
    AdbUtils.pull(src, outFile)
    LoggerUtils.light('>>> ' + outFile)


def doDumpLogger(path):
    LoggerUtils.println('dump log')

    def doDumpLoggerImpl(outFile):
        CmnUtils.doCmd2File('adb logcat -v threadtime', outFile)

    outFile = path + '/log.txt'
    thd = CmnUtils.runThread(doDumpLoggerImpl, outFile, False)
    time.sleep(5)
    LoggerUtils.light('>>> ' + outFile)


def doDumpRuntime(path):
    LoggerUtils.println('dump anr')
    outFile = path + '/anr.txt'
    CmnUtils.doCmd2File('adb pull /data/anr', outFile)
    LoggerUtils.light('>>> ' + outFile)

    LoggerUtils.println('dump ps')
    outFile = path + '/ps.txt'
    CmnUtils.doCmd2File('adb shell ps', path + '/ps.txt')
    LoggerUtils.light('>>> ' + outFile)


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

    LoggerUtils.println('dump app')
    CmnUtils.doCmd2File('adb shell pm list packages -e', path + '/app.txt')


def doDump(env_path, _mode):
    outPath = env_path + os.sep + FileUtils.getTempTimeName('dump_')
    try:
        os.makedirs(outPath)
        if CmnUtils.isEmpty(_mode):
            doDumpUi(outPath)
            doDumpRuntime(outPath)
            doDumpEnv(outPath + os.sep + 'info')
            doDumpSys(outPath + os.sep + 'sys')
            doDumpLogger(outPath)
        elif 'ui' == _mode:
            doDumpUi(outPath)
        elif 'sys' == _mode:
            doDumpSys(outPath + os.sep + 'sys')
        elif 'log' == _mode:
            doDumpLogger(outPath)
        else:
            assert 0, 'Unsupported mode: ' + _mode
        LoggerUtils.println('>>> ' + outPath)
    except Exception as e:
        LoggerUtils.println(e)


def run():
    """
    wing -adb top
    wing -adb pull {package name}
    wing -adb stop {package name}
    wing -adb clear {package name}
    wing -dump
    """
    za = BasicArgumentsValue()
    envPath, spacePath, typ = za.get(0), za.get(1), za.get(2)
    if typ == 'top': return doTopInfo()
    if typ == 'pull': return doPullPackage(envPath, za.get(3))
    if typ == 'stop': return doStopApp(envPath, za.get(3))
    if typ == 'clear': return doClearApp(envPath, za.get(3))
    if typ == 'dump': return doDump(envPath, za.get(3))
    assert 0, 'Unsupported type: ' + typ


if __name__ == "__main__":
    run()
