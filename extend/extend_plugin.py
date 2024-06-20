#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: third plugin
# @date:  2024.05.10 14:40:50

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
#
# local path:
# ${wing root path}/plugin/${plugin name}/*
# ${wing root path}/plugin/${plugin name}/${plugin name}.ver
#

# --------------------------------------------------------------------------------------------------------------------------

def run():
    """
    wing -apktool $@
    wing -jadx $@
    """
    za = BasicArgumentsValue()
    envPath, spacePath, name = za.get(0), za.get(1), za.get(2)
    if name == '-jadx':
        pluginPath = os.path.dirname(g_wing_path) + '/plugin/jadx'
        if not os.path.isfile(pluginPath + '/jadx.ver'):
            LoggerUtils.e('\tjadx not install, run \"wing -update\"')
            return
        CmnUtils.doCmdCall(pluginPath + '/bin/jadx-gui&')
        return
    if name == '-apktool':
        pluginPath = os.path.dirname(g_wing_path) + '/plugin/apktool'
        if not os.path.isfile(pluginPath + '/apktool.ver'):
            LoggerUtils.e('\tapktool not install, run \"wing -update\"')
            return
        CmnUtils.doCmdCall('cd ' + envPath + ' && java -jar ' + pluginPath + '/apktool.jar ' + ' '.join(za.getLast(3)))
        return
    assert 0, 'Unsupported type: ' + name


if __name__ == "__main__":
    run()

