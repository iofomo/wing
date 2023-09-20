# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

from xml import sax
from manager.repo_group import RepoGroup
from manager.repo_project import *


# ----------------------------------------------------------------------------------------------------------------------
class ManifestHandler(sax.ContentHandler):
    """
    <?xml version='1.0' encoding='UTF-8'?>
    <manifest>
        <remote name="origin" fetch=".."/>
        <!-- branch -->
        <default revision="main" remote="origin" sync-j="4"/>
        <!-- basic -->
        <project path="doc" name="xxx/doc"/>
        <!-- export tools -->
        <project path="build" name="xxx/build">
            <copyfile src="build.sh" dest="build.sh"/>
        </project>
    </manifest>
    """

    def __init__(self, path):
        self.mRootPath = path
        self.tag = ""
        self.group = RepoGroup()
        self.depend = None
        self.project = None
        self.projects = []

    def getGroup(self):
        return self.group

    def getProjects(self):
        return self.projects

    def getDependGroup(self):
        return self.depend

    @staticmethod
    def parseXml(path, xml):
        parser = sax.make_parser()
        parser.setFeature(sax.handler.feature_namespaces, 0)
        mh = ManifestHandler(path)
        parser.setContentHandler(mh)
        parser.parse(xml)
        return mh

    def startElement(self, tag, attributes):
        self.tag = tag
        if tag == "default":
            self.group.setRevision(attributes["revision"])
            self.group.setRemote(attributes["remote"])
            self.group.setSyncJ(attributes["sync-j"])
        elif tag == "project":
            self.project = RepoProject()
            self.project.setPath(attributes["path"])
            self.project.setName(attributes["name"])
            if "revision" in attributes: self.project.setRevision(attributes["revision"])
            self.projects.append(self.project)
        elif tag == "copyfile":
            action = RepoProjectActionCopyFile(self.mRootPath)
            action.setSrc(attributes["src"])
            action.setDest(attributes["dest"])
            if 'md5' in attributes: action.setMD5(attributes["md5"])
            assert action.isValid(), 'Invalid action: copyfile'
            self.project.addAction(action)
        elif tag == "removefile":
            action = RepoProjectActionRemoveFile(self.mRootPath)
            action.setDest(attributes["dest"])
            if 'md5' in attributes: action.setMD5(attributes["md5"])
            assert action.isValid(), 'Invalid action: removefile'
            self.project.addAction(action)
        elif tag == "depend":
            if None == self.depend: self.depend = RepoGroup()
            self.depend.setPlatform(attributes["platform"])
            self.depend.setRevision(attributes["revision"])

    # def endElement(self, tag):
    #     if self.tag == "project":
    #         assert self.project != None
    #         print(self.project)
    #         self.project = None

    # def characters(self, content):
    #     if self.CurrentData == "type":
    #         self.type = content
    #     elif self.CurrentData == "format":
    #         self.format = content
    #     elif self.CurrentData == "year":
    #         self.year = content
    #     elif self.CurrentData == "rating":
    #         self.rating = content
    #     elif self.CurrentData == "stars":
    #         self.stars = content
    #     elif self.CurrentData == "description":
    #         self.description = content
