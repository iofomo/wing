#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  read and write *.properties files
# @date:   2023.05.10 14:40:50
import os, sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils


# --------------------------------------------------------------------------------------------------------------------------
class BasicPropertiesItem:

    def __init__(self, k, v=None):
        if None == v: assert k.startswith('#'), 'Invalid key: ' + k
        self.key, self.val = k, v

    def matchKey(self, k):
        return None != self.val and self.key == k

    def matchValue(self, v):
        return self.val == v

    def getKey(self):
        return self.key

    def getValue(self):
        return self.val

    def setValue(self, v):
        assert self.val is not None, 'Invalid value: None'
        self.val = v

    def println(self):
        if None == self.val:
            LoggerUtils.println(self.key)
        else:
            LoggerUtils.println(self.key + '=' + self.val)


class BasicProperties():
    def __init__(self):
        self.properties = []

    def hasKey(self, key):
        assert None != key and 0 < len(key), 'Invalid key: ' + key
        for p in self.properties:
            if p.matchKey(key): return True
        return False

    def get(self, key, default_value=None):
        assert None != key and 0 < len(key), 'Invalid key: ' + key
        for p in self.properties:
            if p.matchKey(key): return p.getValue()
        return default_value

    def put(self, key, value=None):
        assert None != key and 0 < len(key), 'Invalid key: ' + key
        if value is None: assert key.startswith('#')
        for p in self.properties:
            if p.matchKey(key):
                p.setValue(value)
                return
        self.properties.append(BasicPropertiesItem(key, value))

    def remove(self, key):
        assert None != key and 0 < len(key), 'Invalid key: ' + key
        for p in self.properties:
            if p.matchKey(key):
                self.properties.remove(p)
                return

    def load(self, f):
        with open(f, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) <= 0: continue
            if line.startswith('#'):
                self.put(line)
                continue
            pos = line.find('=')
            if pos <= 0: continue
            self.put(line[:pos].strip(), line[pos + 1:])
        return self

    @staticmethod
    def loadFromFile(f):
        items = {}
        with open(f, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) <= 0: continue
            if line.startswith('#'): continue
            pos = line.find('=')
            if pos <= 0: continue
            items[line[:pos].strip()] = line[pos + 1:]
        return items

    @staticmethod
    def loadFromFileWithKey(f, key, defVal=None):
        with open(f, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) <= 0: continue
            if line.startswith('#'): continue
            pos = line.find('=')
            if pos <= 0: continue
            if key != line[:pos].strip(): continue
            return line[pos + 1:]
        return defVal

    def save(self, fileName):
        with open(fileName, 'w') as f:
            for p in self.properties:
                v = p.getValue()
                if None == v:
                    f.write(p.getKey() + '\n')
                else:
                    f.write(p.getKey() + '=' + v + '\n')

    @staticmethod
    def saveToFile(fileName, dictData):
        with open(fileName, 'w') as f:
            for k, v in dictData.items():
                f.write(k + '=' + v + '\n')

    def println(self):
        for p in self.properties: p.println()


def run():
    pass
    # items = BasicProperties.loadFromFile('/Users/xxx/workspace/test.properties')
    # k = items['x2j-column-src']
    # v = items['x2j-column-val']
    # print(k, v)
    # p = BasicProperties()
    # p.put('a', 'b')
    # p.put('a1', 'b1')
    # p.println()
    #
    # assert p.hasKey('a')
    # assert p.hasKey('a1')
    # assert p.get('a') == 'b'
    # assert p.get('a1') == 'b1'
    # p.put('a', 'c')
    # p.println()
    # assert p.get('a') == 'c'
    # p.remove('a')
    # p.println()
    # assert not p.hasKey('a')
    # assert p.get('a') == None


if __name__ == "__main__":
    run()
