#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: Mobile device screen commands
# @date:  2023.05.10 14:40:50

import os
import shutil
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_zip import ZipUtils
from utils.utils_net import NetUtils
from utils.utils_file import FileUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))

BASE_URL_FMT = 'http://www.iofomo.com/download/wing/%s'
# --------------------------------------------------------------------------------------------------------------------------


def checkVersion():
    url = BASE_URL_FMT % 'wing.ver'
    svrVer = NetUtils.downloadContent(url)
    if CmnUtils.isEmpty(svrVer):
        LoggerUtils.e('Connect fail')
        return False

    # wing 1.1.0, (2024.01.01)
    ret = CmnUtils.doCmd("wing -v")
    if CmnUtils.isEmpty(ret): return True# Invalid need install
    items = ret.split(' ')
    if len(items) < 2: return True# Invalid need install

    localVer = items[1][:-1]
    LoggerUtils.println('Local  version: ' + localVer)
    LoggerUtils.println('Remote version: ' + svrVer)

    ll = localVer.split('.')
    ss = svrVer.split('.')

    try:
        if int(ll[0]) < int(ss[0]): return True
        if int(ll[0]) > int(ss[0]): return False
        if int(ll[1]) < int(ss[1]): return True
        if int(ll[1]) > int(ss[1]): return False
        if int(ll[2]) < int(ss[2]): return True
    except Exception as e:
        pass
    return False


def downloadWing():
    tempPath = os.path.dirname(g_wing_path) + '/temp'
    if os.path.exists(tempPath): FileUtils.remove(tempPath)
    if not os.path.exists(tempPath): os.makedirs(tempPath)

    # download
    LoggerUtils.println('download wing ...')
    url = BASE_URL_FMT % 'wing.zip'
    try:
        zFile = tempPath + os.sep + 'wing.zip'
        NetUtils.downloadFileWithProgress(url, zFile)
        LoggerUtils.println('download success')
    except Exception as e:
        print(e)
        return None

    wingPath = tempPath + os.sep + 'wing'
    ZipUtils.unzip(zFile, wingPath)

    setupFile = wingPath + os.sep + "setup.py"
    if not os.path.isfile(setupFile):
        LoggerUtils.e('invalid scrcpy file')
        return None
    return setupFile


def run():
    """
    wing -update
    """
    za = BasicArgumentsValue()
    envPath, spacePath, typ = za.get(0), za.get(1), za.get(2)
    if typ is None:
        if not checkVersion():
            LoggerUtils.println('\nWing already the latest version.\n')
            return
        f = downloadWing()
        if f is None: return
        LoggerUtils.println('do update ...')
        CmnUtils.doCmd('python %s install' % CmnUtils.formatCmdArg(f))
        FileUtils.remove(os.path.dirname(f))
        return
    assert 0, 'Unsupported type: ' + typ


if __name__ == "__main__":
    run()
