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
from utils.utils_cmn import CmnVersion
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_zip import ZipUtils
from utils.utils_net import NetUtils
from utils.utils_file import FileUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))

#
# server files:
# ${base url}/wing.zip
# ${base url}/wing.ver
# ${base url}/plugin/${plugin name}.zip
# ${base url}/plugin/${plugin name}.ver -> 1.0.0.0
#
BASE_URL_FMT = 'https://www.iofomo.com/download/wing/%s'
BASE_URL_ZIP_FMT = 'https://www.iofomo.com/download/wing/plugin/%s.zip'
BASE_URL_VER_FMT = 'https://www.iofomo.com/download/wing/plugin/%s.ver'
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


def downloadWing(tempPath):
    FileUtils.remove(tempPath)
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


def localPluginVersion(name):
    verFile = os.path.dirname(g_wing_path) + ('/plugin/%s/%s.ver' % (name, name))
    if not os.path.isfile(verFile): return None
    with open(verFile) as f: verString = f.readline()
    return CmnVersion(verString.strip())


def checkPluginVersion(name):
    LoggerUtils.println('check ' + name + ' version ...')
    localVer = localPluginVersion(name)
    if localVer is None: return False

    url = BASE_URL_VER_FMT % name
    svrVerString = NetUtils.downloadContent(url)
    if CmnUtils.isEmpty(svrVerString):
        LoggerUtils.e('Connect fail')
        return True

    serverVer = CmnVersion(svrVerString.strip())

    LoggerUtils.println('Local  version: ' + localVer.getVersion())
    LoggerUtils.println('Remote version: ' + serverVer.getVersion())
    return localVer.compare(serverVer) <= 0


def doUpdatePlugin(name, tempPath):
    LoggerUtils.light('%s' % (name))

    if checkPluginVersion(name):
        LoggerUtils.println('%s already the latest version.' % name)
        return True

    FileUtils.remove(tempPath)
    if not os.path.exists(tempPath): os.makedirs(tempPath)

    # download
    LoggerUtils.println('download %s ...' % (name))
    url = BASE_URL_ZIP_FMT % name
    try:
        zFile = tempPath + os.sep + name + '.zip'
        NetUtils.downloadFileWithProgress(url, zFile)
        LoggerUtils.println('download finish')
    except Exception as e:
        print(e)
        return False

    # unzip
    pluginPath = tempPath + os.sep + name
    ZipUtils.unzip(zFile, pluginPath)

    # check
    verFile = pluginPath + os.sep + name + ".ver"
    if not os.path.isfile(verFile):
        LoggerUtils.e('invalid plugin file')
        return False

    # print ver
    with open(verFile, 'r') as f :
        ver = f.readline()
        LoggerUtils.println(name + ': ' + ver)

    # flush
    targetPath = os.path.dirname(g_wing_path) + '/plugin/' + name
    FileUtils.remove(targetPath)
    FileUtils.ensureFileDir(targetPath)
    os.rename(pluginPath, targetPath)

    # return
    if not os.path.isfile(targetPath + os.sep + name + ".ver"):
        LoggerUtils.e('Invalid file')
        return False

    CmnUtils.doCmd('chmod -R +x ' + targetPath)

    LoggerUtils.println('update success')
    return True

def doUpdateWing(tempPath):
    LoggerUtils.light('wing')
    if not checkVersion():
        LoggerUtils.println('\nWing already the latest version.\n')
        return
    f = downloadWing(tempPath)
    if f is None: return
    LoggerUtils.println('do update wing ...')
    CmnUtils.doCmd('python %s install' % CmnUtils.formatCmdArg(f))
    FileUtils.remove(os.path.dirname(f))

def showHelp():
    LoggerUtils.println('wing -update [jadx/apktool/mobtool]')

def run():
    """
    wing -update
    wing -update jadx
    wing -update apktool
    wing -update mobtool
    """
    za = BasicArgumentsValue()
    envPath, spacePath, typ = za.get(0), za.get(1), za.get(2)
    if typ is None: showHelp()

    tempPath = os.path.dirname(g_wing_path) + '/temp'
    try:
        doUpdateWing(tempPath)
        if typ == 'jadx':
            doUpdatePlugin('jadx', tempPath)
        elif typ == 'apktool':
            doUpdatePlugin('apktool', tempPath)
        elif typ == 'mobtool':
            doUpdatePlugin('mobtool', tempPath)
        elif typ is not None:
            LoggerUtils.w('UNSupport plugin: ' + typ)
        # add more plugin here ...
    except Exception as e:
        LoggerUtils.e(e)
    finally:
        FileUtils.remove(tempPath)

if __name__ == "__main__":
    run()
