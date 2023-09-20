#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: parse xml file
# @date:   2023.05.10 14:40:50

from xml.dom.minidom import parse


# --------------------------------------------------------------------------------------------------------------------------
class BasicXmlReader:
    def __init__(self, xmlFile):
        domTree = parse(xmlFile)
        self.mRootNode = domTree.documentElement

    def getElements(self, tag):
        return self.mRootNode.getElementsByTagName(tag)

    def getElementAttribute(self, e, attrKey):
        if e.hasAttribute(attrKey): return e.getAttribute(attrKey)
        return None

    def getAttributeByElementIndex(self, eleTag, index, attrKey):
        ee = self.getElements(eleTag)
        if None == ee: return None
        if index < 0 or len(ee) <= index: return None
        if ee[index].hasAttribute(attrKey): return ee[index].getAttribute(attrKey)
        return None

    @staticmethod
    def readAttributeByElementIndex(xmlFile, eleTag, index, attrKey):
        return BasicXmlReader(xmlFile).getAttributeByElementIndex(eleTag, index, attrKey)
