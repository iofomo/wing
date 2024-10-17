#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  pack and publish to iofomo.com/download/wing
#          python build.py pack
#          python build.py publish
# @author: iofomo
# @date:   2024.01.03 14:40:50

import sys, os, shutil

g_env_path = os.getcwd()
g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
# --------------------------------------------------------------------------------------------------------------------------
# init project env
g_wing_path = os.path.expanduser("~") + os.sep + '.wing/wing' #  such as: /Users/${username}/.wing/wing
sys.path.append(g_wing_path)
from utils.utils_import import ImportUtils
g_space_path = ImportUtils.initSpaceEnv(g_env_path)

from utils.utils_cmn import CmnUtils
from utils.utils_zip import ZipUtils
from utils.utils_file import FileUtils
from utils.utils_logger import LoggerUtils
# --------------------------------------------------------------------------------------------------------------------------


def doZip(srcDir, desZipFile, ignoreDirs, ignoreFiles):
    assert os.path.exists(srcDir)
    if os.path.exists(desZipFile): os.remove(desZipFile)
    try:
        if None == ignoreDirs: ZipUtils.zipDir(srcDir, desZipFile)
        elif None == ignoreFiles: ZipUtils.zipDir(srcDir, desZipFile, ignoreDirs)
        else: ZipUtils.zipDir(srcDir, desZipFile, ignoreDirs, ignoreFiles)
        assert os.path.exists(desZipFile)
        # print('done: ' + os.path.basename(desZipFile))
        return
    except Exception as e:
        LoggerUtils.println(e)
    if os.path.exists(desZipFile): os.remove(desZipFile)


def cleanBuildDirs(path):
    dd = []
    tmps = ['__MACOSX', 'build', '__pycache__']
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir in tmps: dd.append(os.path.join(root, dir))
            elif dir.startswith('.'): dd.append(os.path.join(root, dir))
        for f in files:
            if f.startswith('.'): dd.append(os.path.join(root, f))
            elif f.endswith('.pyc'): dd.append(os.path.join(root, f))
            elif f in ['cache.json','cacher.json']: dd.append(os.path.join(root, f))
    for d in dd: FileUtils.remove(d)


def doCleanByProject(path):
    cleanBuildDirs(path)


def doMake(inPath, outFile, cb):
    path = os.path.dirname(outFile)
    if not os.path.exists(path): os.makedirs(path)
    path += os.sep + FileUtils.getTempName('.tmp_')
    try:
        CmnUtils.doCmd('rm -rf ' + path + '*')
        shutil.copytree(inPath, path)
        cb(path)
        doZip(path, outFile, None, None)
        return
    except Exception as e:
        LoggerUtils.println(e)
    finally:
        FileUtils.remove(path)
    assert 0, 'Copy exception: ' + path


def getWingVer():
    with open(g_this_path + os.sep + 'wing.py', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if CmnUtils.isEmpty(line): continue
            if not line.startswith('g_ver'): continue
            pos1 = line.find("'")
            pos2 = line.rfind("'")
            ver = line[pos1+1:pos2]
            LoggerUtils.println(' ver: ' + ver)
            return ver
    assert 0, 'Version not found'


def run():
    if len(sys.argv) < 2:
        print('The most similar command is:')
        print('         pack')
        print('         publish')
        print('         publish <plugin file>')
        return

    wingFile = os.path.dirname(g_this_path) + '/wing.zip'
    verFile = os.path.dirname(g_this_path) + '/wing.ver'
    # build.py pack
    if sys.argv[1] == 'pack':
        doMake(g_this_path, wingFile, doCleanByProject)
        LoggerUtils.println('>>> ' + wingFile)
        with open(verFile, 'w') as f: f.write(getWingVer())
        LoggerUtils.println('>>> ' + verFile)
        LoggerUtils.light('\ndone.\n')
        return
    if sys.argv[1] == 'publish':
        # TODO upload to server
        return
    assert 0, 'UNsupport type: ' + sys.argv[1]

if __name__ == "__main__":
    run()
