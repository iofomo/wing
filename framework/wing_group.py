#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

from utils.utils_logger import LoggerUtils


# -------------------------------------------------------------
class WingGroup:
    """
    <default revision="main" remote="origin" sync-j="4"/>
    """

    def __init__(self):
        self.revision = ""
        self.remote = ""
        self.syncj = ""
        self.platform = ""

    def setPlatform(self, v): self.platform = v

    def getPlatform(self): return self.platform

    def setRevision(self, v): self.revision = v

    def getRevision(self): return self.revision

    def setRemote(self, v): self.remote = v

    def getRemote(self): return self.remote

    def setSyncJ(self, v): self.syncj = v

    def getSyncJ(self): return self.syncj

    def println(self):
        LoggerUtils.println('syncj: ' + self.syncj)
        LoggerUtils.println('remote: ' + self.remote)
        LoggerUtils.println('revision: ' + self.revision)
