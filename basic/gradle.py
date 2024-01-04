#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  gradle project info parser
# @date:   2023.05.10 14:40:50

import os, re, sys

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils


# --------------------------------------------------------------------------------------------------------------------------
class BasicGradle:
    """
        parse Android studio project
    """

    def __init__(self, path):
        self.mPath = path
        self.mPackageName = None
        self.mModules = []
        if not BasicGradle.isGradleProject(self.mPath): return
        self.__parse_modules__()
        self.__parse_pkg_name__()

    @staticmethod
    def isGradleProject(path):
        return os.path.isfile(path + os.sep + 'settings.gradle') and os.path.isfile(path + os.sep + 'build.gradle')

    def __parse_modules__(self):
        with open(self.mPath + '/settings.gradle', 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('//'): continue
            items = re.findall(r"\'\:(\S+?)\'", line)
            for item in items:
                # if 0 < item.find(':'): continue  # ignore sub module
                self.mModules.append(item.replace(':', '/'))
            items = re.findall(r"\"\:(\S+?)\"", line)
            for item in items:
                # if 0 < item.find(':'): continue  # ignore sub module
                self.mModules.append(item.replace(':', '/'))

    def getMode(self, module):
        """
        apply plugin: 'com.android.library'
        applicationId rootProject.ext.packageName
        apply plugin: 'com.android.application'
        apply plugin: 'java'
        """
        path = self.mPath + os.sep + module + '/build.gradle'
        if not os.path.isfile(path): return None
        with open(path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith('apply plugin:'):
                if 0 < line.find('com.android.library'): return 'aar'
                if 0 < line.find('com.android.application'): return 'apk'
                if 0 < line.find('java'): return 'jar'
                LoggerUtils.println('warning: ' + line)
                return None
            if line.startswith('applicationId '): return 'apk'
        return None

    def __parse_pkg_name__(self):
        while True:
            fname = self.mPath + '/app/build.gradle'
            if os.path.exists(fname): break
            fname = self.mPath + '/demo/build.gradle'
            if os.path.exists(fname): break
            fname = self.mPath + '/client/build.gradle'
            if os.path.exists(fname): break
            # print('Not found application module, maybe java project !!!')
            return

        with open(fname, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line.startswith('applicationId '): continue
            self.mPackageName = re.findall(r'\"(\S+?)\"', line)[0]
            break

    def isValid(self):
        return 0 < len(self.getPackageName()) or 0 < len(self.mModules)

    def getPackageName(self):
        return self.mPackageName if None != self.mPackageName else ""

    def isProjectAndroid(self):
        return 0 < len(self.getPackageName())

    def isProjectJava(self):
        return len(self.getPackageName()) <= 0

    def getModules(self):
        return self.mModules

    def getModulePath(self, module):
        return self.mPath + os.sep + module.replace(':', '/')

    def getJTestModules(self):
        modules = []
        for module in self.mModules:
            if os.path.exists(self.mPath + os.sep + module + '/src/test'): modules.append(module)
        return modules

    def getAndroidTestModules(self):
        modules = []
        for module in self.mModules:
            if os.path.exists(self.mPath + os.sep + module + '/src/androidTest'): modules.append(module)
        return modules

    def getPublishModules(self):
        modules = []
        for module in self.mModules:
            fname = self.mPath + os.sep + module + '/build.gradle'
            if not os.path.exists(fname): continue
            with open(fname, 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line.startswith('apply plugin'): continue
                modules.append(module)
                break
        return modules

    def getCheckModules(self):
        modules = []
        for module in self.mModules:
            fname = self.mPath + os.sep + module + '/build.gradle'
            if not os.path.exists(fname): continue
            modules.append(module)
        return modules

    def println(self):
        LoggerUtils.println('mPath: ' + self.mPath)
        LoggerUtils.println('mPackageName: ' + self.getPackageName())
        for i in range(len(self.mModules)):
            LoggerUtils.println('module[%d]: %s' % (i + 1, self.mModules[i]))


def run():
    g = BasicGradle('/Users/xxx/workspace/xxx/abc')
    g.println()
    print(g.isValid())
    print(g.getAndroidTestModules())
    print(g.getJTestModules())
    print(g.getPublishModules())
    print(g.getCheckModules())


if __name__ == "__main__":
    run()
