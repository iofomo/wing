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

BASE_URL_FMT = 'http://www.iofomo.com/download/scrcpy/scrcpy-%s'
# --------------------------------------------------------------------------------------------------------------------------
def doScreen():
    AdbUtils.ensureEnv()
    sysEnv = isEnvOK()
    if not sysEnv:
        binFile = getBinFile()
        if None == binFile: return

    dd = AdbUtils.getDevices()
    # print(dd)
    if CmnUtils.isEmpty(dd):
        LoggerUtils.e('No devices found')
        return
    if sysEnv:
        for d in dd: CmnUtils.doCmd("scrcpy -s " + d + " &")
        return

    if binFile is None: return
    for d in dd: CmnUtils.doCmd('%s -s %s &' % (CmnUtils.formatCmdArg(binFile), d))

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
    wing -screen
    """
    za = BasicArgumentsValue()
    envPath, spacePath, typ = za.get(0), za.get(1), za.get(2)
    if typ is None: return doScreen()
    assert 0, 'Unsupported type: ' + typ


if __name__ == "__main__":
    run()
