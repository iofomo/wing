#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, shutil
from utils.utils_logger import LoggerUtils
from utils.utils_cmn import CmnUtils


# ----------------------------------------------------------------------------------------------------------------------
class RepoProjectAction:
    def __init__(self, path):
        self.mRootPath = path

    def isValid(self):
        return False

    def doAction(self, project, force):
        pass

    def isTargetFile(self, destFile, force):
        if force: return True
        if None == self.md5: return False
        lclmd5 = CmnUtils.md5File(destFile)
        md5s = self.md5.split(',')
        for m in md5s:
            if m == lclmd5: return True  # md5 target match
        return False  # md5 not match

    def println(self):
        LoggerUtils.println('mRootPath: ' + self.mRootPath)


class RepoProjectActionCopyFile(RepoProjectAction):
    """
    local file exist, then ignore
    <copyfile src="build.sh" dest="build.sh"/>
    local file exist, then check md5, match then replaced, otherwise ignore
    <copyfile src="build.sh" dest="build.sh" md5="607fe3d79156f549ee240c24842a299b"/>
    """

    def __init__(self, path):
        RepoProjectAction.__init__(self, path)
        self.src, self.dest, self.md5 = '', '', None

    def isValid(self):
        return 0 < len(self.src) and 0 < len(self.dest)

    def setSrc(self, v):
        self.src = v

    def getSrc(self):
        return self.src

    def setDest(self, v):
        self.dest = v

    def getDest(self):
        return self.dest

    def setMD5(self, v):
        self.md5 = v.strip()

    def getMD5(self):
        return self.md5

    def doAction(self, project, force):
        sf = project.getPath() + os.sep + self.src
        s = self.mRootPath + os.sep + sf
        if not os.path.isfile(s): return
        d = self.mRootPath + os.sep + self.dest

        # if os.path.isfile(d) and not self.isTargetFile(d, force): return  # exist then check replace

        dr = os.path.dirname(d)
        if not os.path.isdir(dr): os.makedirs(dr)
        assert os.path.isdir(dr), 'Make dirs fail: ' + dr
        shutil.copyfile(s, d)
        assert os.path.isfile(d), 'Copy file fail: ' + d
        CmnUtils.doCmd('chmod a+x ' + d)
        LoggerUtils.light('export: ' + sf + ' -> ' + d)

    def println(self):
        RepoProjectAction.println(self)
        LoggerUtils.println('src: ' + self.src)
        LoggerUtils.println('dest: ' + self.dest)
        LoggerUtils.println('md5: ' + ('' if None == self.md5 else self.md5))


class RepoProjectActionRemoveFile(RepoProjectAction):
    """
    local file exist, then ignore
    <copyfile src="build.sh" dest="build.sh"/>
    local file exist, then check md5, match then replaced, otherwise ignore
    <copyfile src="build.sh" dest="build.sh" md5="607fe3d79156f549ee240c24842a299b"/>
    """

    def __init__(self, path):
        RepoProjectAction.__init__(self, path)
        self.dest, self.md5 = '', None

    def isValid(self):
        return 0 < len(self.dest)

    def setDest(self, v):
        self.dest = v

    def getDest(self):
        return self.dest

    def setMD5(self, v):
        self.md5 = v

    def getMD5(self):
        return self.md5

    def doAction(self, project, force):
        d = self.mRootPath + os.sep + self.dest
        if not os.path.isfile(d): return  # not exist, then ignore
        if not self.isTargetFile(d, force): return

        os.remove(d)
        assert not os.path.isfile(d), 'Remove file fail:' + d
        LoggerUtils.light('remove: ' + d)

    def println(self):
        RepoProjectAction.println(self)
        LoggerUtils.println('dest: ' + self.dest)
        LoggerUtils.println('md5: ' + self.md5)


class RepoProject:
    """
    <project path="build" name="xxx/build">
        <copyfile src="build.sh" dest="build.sh"/>
    </project>
    """

    def __init__(self):
        self.path = ""  # code from server
        self.name = ""  # code to local
        self.revision = ""  # code to local
        self.actions = []

    def isValid(self):
        if len(self.path) <= 0 or len(self.name) <= 0: return False
        for a in self.actions:
            if not a.isValid():
                return False
        return True

    def reset(self):
        self.path = ""  # code from server
        self.name = ""  # code to local
        self.actions = []

    def setPath(self, v):
        self.path = v

    def getPath(self):
        return self.path

    def setName(self, v):
        self.name = v

    def getName(self):
        return self.name

    def setRevision(self, v):
        self.revision = v

    def getRevision(self):
        return self.revision

    def addAction(self, v):
        self.actions.append(v)

    def doActions(self, force):
        for a in self.actions:
            try:
                a.doAction(self, force)
            except Exception as e:
                LoggerUtils.exception(e)

    def println(self):
        LoggerUtils.println('path: ' + self.path)
        LoggerUtils.println('name: ' + self.name)
        LoggerUtils.println('revision: ' + self.revision)
        for action in self.actions: action.println()
