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

g_env_path, g_this_file, g_this_path = ImportUtils.initEnv()
g_repo_path = ImportUtils.initPath(g_env_path)


# --------------------------------------------------------------------------------------------------------------------------
class ExtendClean:
    def __init__(self, repoPath, envPath):
        self.mRepoPath, self.mEnvPath = repoPath, envPath
        self.mProjPath = self.__getProjectPath__(envPath)

    def __getProjectPath__(self, path):
        while 1 < len(path):
            if os.path.exists(path + '/.git/config'): return path  # for git
            if os.path.exists(path + '/build.gradle'): return path  # for gradle
            path = os.path.dirname(path)
        return None

    def __getAllGits__(self):
        projects = []
        self.findSubs(self.mRepoPath, projects, '/.git/config')
        return projects

    def findSubs(self, root, projects, sub, level=0):
        if 2 < level: return
        if not os.path.isdir(root): return
        dd = os.listdir(root)
        if None == dd: return
        for d in dd:
            path = root + os.sep + d
            if os.path.exists(path + sub):
                projects.append(path[len(self.mRepoPath) + 1:])
                continue
            self.findSubs(path, projects, sub, level + 1)

    def __getAllGradles__(self):
        projects = []
        self.findSubs(self.mRepoPath, projects, '/build.gradle')
        return projects

    def doClean(self, typ):
        if None == self.mProjPath or os.path.normcase(self.mRepoPath) == os.path.normcase(self.mProjPath):
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
            name = self.mProjPath[len(self.mRepoPath) + 1:]
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
        path = self.mRepoPath + os.sep + name
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
        path = self.mRepoPath + os.sep + name
        git = BasicGit(self.mRepoPath, path)
        bb = git.getOtherBranches()
        for b in bb:
            if b in ['develop', 'main', 'master']: continue
            git.deleteBranch(b)
            LoggerUtils.println('delete: ' + b)
        git.cleanCache()


def run():
    """
    repo -clean gradle
    repo -clean git
    repo -clean py
    """
    if len(sys.argv) <= 3:
        LoggerUtils.println('The most similar command is')
        LoggerUtils.println('    repo -clean gradle')
        LoggerUtils.println('    repo -clean git')
        LoggerUtils.println('    repo -clean py')
        return
    envPath, typ = sys.argv[2], sys.argv[3]
    zc = ExtendClean(g_repo_path, envPath)
    zc.doClean(typ)


if __name__ == "__main__":
    run()
