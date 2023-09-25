#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: clean gradle and git cache
# @date:   2023.05.10 14:40:50

import sys, os

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from basic.git import BasicGit
from basic.arguments import BasicArgumentsValue

ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
class ExtendClean:
    def __init__(self, spacePath, envPath):
        self.mSpacePath, self.mEnvPath = spacePath, envPath
        self.mProjPath = self.__getProjectPath__(envPath)

    def __getProjectPath__(self, path):
        while 1 < len(path):
            if os.path.exists(path + '/.git/config'): return path  # for git
            if os.path.exists(path + '/build.gradle'): return path  # for gradle
            path = os.path.dirname(path)
        return None

    def __getAllGits__(self):
        projects = []
        self.findSubs(self.mSpacePath, projects, '/.git/config')
        return projects

    def findSubs(self, root, projects, sub, level=0):
        if 2 < level: return
        if not os.path.isdir(root): return
        dd = os.listdir(root)
        if None == dd: return
        for d in dd:
            path = root + os.sep + d
            if os.path.exists(path + sub):
                projects.append(path[len(self.mSpacePath) + 1:])
                continue
            self.findSubs(path, projects, sub, level + 1)

    def __getAllGradles__(self):
        projects = []
        self.findSubs(self.mSpacePath, projects, '/build.gradle')
        return projects

    def doClean(self, typ):
        if None == self.mProjPath or os.path.normcase(self.mSpacePath) == os.path.normcase(self.mProjPath):
            if 'git' == typ:
                projects = self.__getAllGits__()
                for project in projects: self.__doCleanGit__(project)
            elif 'gradle' == typ:
                projects = self.__getAllGradles__()
                for project in projects: self.__doCleanGradle__(project)
                self.__doCleanGradleGlobal__()
            elif 'py' == typ:
                self.__doCleanPythonProject__()
        else:
            name = self.mProjPath[len(self.mSpacePath) + 1:]
            if 'git' == typ:
                self.__doCleanGit__(name)
            elif 'gradle' == typ:
                self.__doCleanGradle__(name)
            elif 'py' == typ:
                self.__doCleanPythonProject__()

    def __doCleanPythonProject__(self):
        LoggerUtils.println(self.mEnvPath)
        for root, dirs, files in os.walk(self.mEnvPath):
            for f in files:
                if not f.endswith('.pyc'): continue
                f = os.path.join(root, f)
                FileUtils.remove(f)
                LoggerUtils.light('clean: ' + f)

    def __doCleanGradle__(self, name):
        path = self.mSpacePath + os.sep + name
        gfile = path + os.sep + 'gradlew'
        if not os.path.isfile(gfile): return
        LoggerUtils.println('>>> Clean gradle: ' + name)
        CmnUtils.doCmd('chmod a+x %s ' % gfile)
        ret = CmnUtils.doCmdCall('cd %s && ./gradlew build --refresh-dependencies' % path)
        assert 0 == ret or '0' == ret, 'Gradle refresh cache fail: ' + name

    def __doCleanGradleGlobal__(self):
        LoggerUtils.println('>>> Clean gradle global cache')
        cachePath = CmnUtils.getOSUserPath() + os.sep + '.gradle'
        # clean log files
        for root, dirs, files in os.walk(cachePath):
            for f in files:
                if not f.endswith('.log'): continue
                f = os.path.join(root, f)
                os.remove(f)
                LoggerUtils.w('delete: ' + f)

    def __doCleanGit__(self, name):
        LoggerUtils.println('>>> Clean git: ' + name)
        path = self.mSpacePath + os.sep + name
        git = BasicGit(path)
        bb = git.getOtherBranches()
        for b in bb:
            if b in ['develop', 'main', 'master']: continue
            git.deleteBranch(b)
            LoggerUtils.println('delete: ' + b)
        git.cleanCache()


def run():
    """
    wing -clean gradle
    wing -clean git
    wing -clean py
    """
    if len(sys.argv) <= 3:
        LoggerUtils.println('The most similar command is')
        LoggerUtils.println('    wing -clean gradle')
        LoggerUtils.println('    wing -clean git')
        LoggerUtils.println('    wing -clean py')
        return

    za = BasicArgumentsValue()
    envPath, spacePath, typ = za.get(0), za.get(1), za.get(2)
    zc = ExtendClean(spacePath, envPath)
    zc.doClean(typ)


if __name__ == "__main__":
    run()
