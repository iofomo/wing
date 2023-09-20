#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: parse config of .repo project
# @date:   2023.05.10 14:40:50
import os, sys
from xml import sax

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from basic.xmlreader import BasicXmlReader


# --------------------------------------------------------------------------------------------------------------------------
class BasicRepoManifestGroup:
    """
    <default revision="main" remote="origin" sync-j="4"/>
    """

    def __init__(self):
        self.revision = ""
        self.remote = ""
        self.syncj = ""
        self.depend_platform = ""
        self.depend_revision = ""

    def setRevision(self, v): self.revision = v

    def getRevision(self): return self.revision

    def setRemote(self, v): self.remote = v

    def getRemote(self): return self.remote

    def setSyncJ(self, v): self.syncj = v

    def getSyncJ(self): return self.syncj

    def setDependPlatform(self, v): self.depend_platform = v

    def getDependPlatform(self): return self.depend_platform

    def setDependRevision(self, v): self.depend_revision = v

    def getDependRevision(self): return self.depend_revision

    def println(self):
        LoggerUtils.println('syncj: ' + self.syncj)
        LoggerUtils.println('remote: ' + self.remote)
        LoggerUtils.println('revision: ' + self.revision)


class BasicRepoManifestProject:
    """
    <project path="build" name="xxx/build">
        <copyfile src="build.sh" dest="build.sh"/>
    </project>
    """

    def __init__(self):
        self.path = ""  # code from server
        self.name = ""  # code to local
        self.revision = ""  # code to local

    def isValid(self):
        if len(self.path) <= 0 or len(self.name) <= 0: return False
        return True

    def reset(self):
        self.path = ""  # code from server
        self.name = ""  # code to local

    def setPath(self, v): self.path = v

    def getPath(self): return self.path

    def setName(self, v): self.name = v

    def getName(self): return self.name

    def setRevision(self, v): self.revision = v

    def getRevision(self): return self.revision

    def println(self):
        LoggerUtils.println('path: ' + self.path)
        LoggerUtils.println('name: ' + self.name)
        LoggerUtils.println('revision: ' + self.revision)


class BasicRepoManifest(sax.ContentHandler):
    """
    <?xml version='1.0' encoding='UTF-8'?>
    <manifest>
        <remote name="origin" fetch=".."/>
        <!-- branch -->
        <default revision="master" remote="origin" sync-j="4"/>
        <!-- basic -->
        <project path="doc" name="xxx/doc"/>
        <!-- export tools -->
        <project path="build" name="xxx/build">
            <copyfile src="build.sh" dest="build.sh"/>
        </project>
    </manifest>
    """

    def __init__(self, xml):
        self.tag = ""
        self.group = BasicRepoManifestGroup()
        self.project = None
        self.projects = []
        self.__doParseXml(xml)

    def getGroup(self):
        return self.group

    def getProjects(self):
        return self.projects

    def __doParseXml(self, xml):
        parser = sax.make_parser()
        parser.setFeature(sax.handler.feature_namespaces, 0)
        parser.setContentHandler(self)
        parser.parse(xml)

    def startElement(self, tag, attributes):
        self.tag = tag
        if tag == "default":
            self.group.setRevision(attributes["revision"])
            self.group.setRemote(attributes["remote"])
            self.group.setSyncJ(attributes["sync-j"])
        elif tag == "project":
            self.project = BasicRepoManifestProject()
            self.project.setPath(attributes["path"])
            self.project.setName(attributes["name"])
            if "revision" in attributes: self.project.setRevision(attributes["revision"])
            self.projects.append(self.project)
        elif tag == "depend":
            self.group.setDependPlatform(attributes["platform"])
            self.group.setDependRevision(attributes["revision"])


class BasicRepoIn:
    def __init__(self, repoPath):
        self.mConfig = {}
        self.mPath = repoPath
        self.mManifest = None
        sys.path.append(repoPath + '/python/')

    def __parse_config__(self):
        jrepo = FileUtils.loadJsonByFile(self.mPath + '/.repo/cache.json')
        assert 'group' in jrepo, 'Invalid repo project !!!'
        self.mConfig['group'] = jrepo['group']
        if 'name' in jrepo: self.mConfig['name'] = jrepo['name']
        if 'branch' in jrepo: self.mConfig['branch'] = jrepo['branch']
        if 'manifest' in jrepo:
            self.mConfig['manifest'] = jrepo['manifest']
        else:
            self.mConfig['manifest'] = self.__parse_manifest__()

    def __parse_manifest__(self):
        xr = BasicXmlReader(self.mPath + '/.repo/manifest.xml')
        return xr.getAttributeByElementIndex('include', 0, 'name')

    def __getItem__(self, k):
        if len(self.mConfig) <= 0: self.__parse_config__()
        if k in self.mConfig: return self.mConfig[k]
        return None

    def updateBranch(self, branch):
        if len(self.mConfig) <= 0: self.__parse_config__()
        self.mConfig['branch'] = branch
        FileUtils.saveJsonToFile(self.mPath + '/.repo/config.json', self.mConfig)

    def getGroup(self):
        return self.__getItem__('group')

    def getName(self):
        return self.__getItem__('name')

    def getManifest(self):
        return self.__getItem__('manifest')

    def getManifestFile(self):
        return self.mPath + '/.repo/manifests/' + self.getManifest()

    def getBranch(self):
        return self.__getItem__('branch')

    def getDependRevision(self):
        return self.__get_manifest__().getGroup().getDependRevision()

    def getDependPlatform(self):
        return self.__get_manifest__().getGroup().getDependPlatform()

    def getManifestProjects(self):
        return self.__get_manifest__().getProjects()

    def __get_manifest__(self):
        if None == self.mManifest:
            self.mManifest = BasicRepoManifest(self.getManifestFile())
        return self.mManifest

    def println(self):
        if len(self.mConfig) <= 0: self.__parse_config__()
        for k, v in self.mConfig.items(): LoggerUtils.println(k + ': ' + v)


def run():
    BasicRepoIn('/Users/xxx/workspace/demo').println()


if __name__ == "__main__":
    run()
