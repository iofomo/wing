#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: Mobile device screen commands
# @date:  2023.05.10 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_file import FileUtils
from utils.utils_zip import ZipUtils
from utils.utils_net import NetUtils
from utils.utils_adb import AdbUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))

BASE_URL_FMT = 'http://www.iofomo.com/download/wing/plugin/scrcpy/scrcpy-%s'
# --------------------------------------------------------------------------------------------------------------------------
def doEnvPrepare():
    AdbUtils.ensureEnv()
    sysEnv = isEnvOK()
    if not sysEnv:
        binFile = getBinFile()
        return sysEnv, binFile
    return sysEnv, None


def doLaunchDevice(sysEnv, binFile, did):
    LoggerUtils.println('Launch device: ' + did)
    if sysEnv:
        CmnUtils.doCmd("scrcpy -s " + did + " &")
    elif binFile is not None:
        CmnUtils.doCmd('%s -s %s &' % (CmnUtils.formatCmdArg(binFile), did))
    else:
        LoggerUtils.e('scrcpy not found')


def doScreen(dids):
    sysEnv, binFile = doEnvPrepare()
    if CmnUtils.isEmpty(dids):
        dids = AdbUtils.getDevices()
    # print(dids)
    if CmnUtils.isEmpty(dids):
        LoggerUtils.e('No devices found')
        return
    if sysEnv is None and binFile is None:
        LoggerUtils.e('scrcpy not found')
        return

    for did in dids:
        doLaunchDevice(sysEnv, binFile, did)


def isEnvOK():
    ret = CmnUtils.doCmd("scrcpy -v")
    return 0 <= ret.find('scrcpy')

def getFileName():
    if CmnUtils.isOsWindows(): return 'win-x64.zip'
    if CmnUtils.isOsMac(): return 'mac-x64.dmg'
    return 'linux-x64.zip'

def getBinFile():
    binFile = os.path.dirname(g_this_path) + '/plugin/scrcpy/scrcpy'
    if CmnUtils.isOsWindows(): binFile += '.exe'
    elif CmnUtils.isOsMac(): binFile = '/Applications/QtScrcpy.app/Contents/MacOS/QtScrcpy'
    if os.path.isfile(binFile): return binFile

    # download
    LoggerUtils.println('download scrcpy ...')
    url = BASE_URL_FMT % getFileName()
    try:
        zPath = os.path.dirname(g_this_path) + '/plugin'
        if not os.path.exists(zPath): os.makedirs(zPath)
        zFile = zPath + os.sep + getFileName()
        NetUtils.downloadFileWithProgress(url, zFile)
        LoggerUtils.println('download success')
    except Exception as e:
        print(e)
        return None

    if CmnUtils.isOsMac():
        CmnUtils.doCmd("open " + zFile)# install
        LoggerUtils.println('manual install')
    else:
        ZipUtils.unzip(zFile, os.path.dirname(binFile))
        if os.path.isfile(binFile): return binFile
        LoggerUtils.e('invalid scrcpy file')
    return None

def run():
    """
    wing -screen [device id]
    """
    za = BasicArgumentsValue()
    envPath, spacePath = za.get(0), za.get(1)
    return doScreen(za.getLast(2))
    # assert 0, 'Unsupported type: ' + typ


if __name__ == "__main__":
    run()
