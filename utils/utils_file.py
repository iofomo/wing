#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for file I/O
# @date:   2023.08.10 14:40:50

import os, sys, time, json, shutil
from fnmatch import fnmatchcase
from utils.utils_logger import LoggerUtils
from utils.utils_cmn import CmnUtils

# -------------------------------------------------------------
class FileUtils:
    g_temp_file_index = 0

    @staticmethod
    def getModifyTime(f):
        if os.path.exists(f):
            try:
                return int(os.path.getmtime(f) * 1000000)
            except Exception as e:
                LoggerUtils.println(e)
        return 0

    @staticmethod
    def ensureDir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def ensureFileDir(f):
        FileUtils.ensureDir(os.path.dirname(f))

    @classmethod
    def getTempName(cls, pre=None, end=None):
        if pre is None: pre = ''
        if end is None: end = ''
        v = int(time.time() * 10)
        cls.g_temp_file_index += 1
        return '%s%ld%d%s' % (pre, v, cls.g_temp_file_index, end)

    @classmethod
    def getTempTimeName(cls, pre=None, end=None):
        tname = time.strftime('%Y%m%d_%H%M%S')
        return ('' if pre is None else pre) + tname + ('' if end is None else end)

    @staticmethod
    def getFileTailName(name, tail):
        """
        :param name: "/home/test.txt"
        :param tail: "xxx"
        :return: "/home/testxxx.txt"
        """
        ss = os.path.splitext(name)
        if 1 < len(ss):
            l = len(ss[-1])
            if 0 < l: return name[:-l] + tail + ss[-1]
        return name + tail

    @staticmethod
    def getUniqueFile(name, suffix=''):
        """
        :param name: /home/demo.txt
        :return: /home/demo(1).txt
        """
        if not os.path.isfile(name): return name

        pos1 = -1
        fName = os.path.basename(name)
        try:
            pos1 = fName.rfind('.')
        except Exception as e:
            pass
        # print(pos1)
        if 0 <= pos1:
            pos1 = pos1 - len(fName)
            name = name[:pos1] + suffix + '(%d)' + name[pos1:]
        else:
            name = name + suffix + '(%d)'
        # print(name)
        i = 1
        while True:
            path = name % i
            if not os.path.exists(path): return path
            i += 1

    @staticmethod
    def loadJsonByFile(name):
        if CmnUtils.isEmpty(name): return None
        try:
            if not os.path.isfile(name): return None
            with open(name, 'rb') as f: content = f.read()
            #json.loads(content, ensure_ascii=False)
            return json.loads(content)
        except Exception as e:
            LoggerUtils.println(e)
        return None

    @staticmethod
    def saveJsonToFile(name, content):
        try:
            # json.dumps(content, ensure_ascii=False)
            jcntt = json.dumps(content)
            path = os.path.dirname(name)
            if not os.path.isdir(path): os.makedirs(path)
            with open(name, 'w') as f: f.write(jcntt)
            return True
        except Exception as e:
            LoggerUtils.println(e)
        return False

    @staticmethod
    def saveLog(path, msg):
        FileUtils.ensureDir(path)
        name = 'log_' + time.strftime('%Y%m%d_%H%M%S')
        fullName = path + os.path.sep + name
        with open(fullName, 'w') as f: f.write(msg)
        return fullName

    @staticmethod
    def parseFileNameAndExt(f):
        items = os.path.splitext(os.path.basename(f))
        if 1 < len(items): return items[0], items[1]
        return items[0], None

    @staticmethod
    def getFileExt(f):
        items = os.path.splitext(os.path.basename(f))
        if 1 < len(items): return items[1]
        return None

    @staticmethod
    def copyFileByPattern(fromFileFmt, toPath):
        """
        "cp -f /home/out/src/*.jar /home/out/des"
        :param fromFileFmt: "/home/out/src/*.jar"
        :param toPath: "/home/out/des"
        """
        if not os.path.isdir(toPath): os.makedirs(toPath)

        fromPath = os.path.dirname(fromFileFmt)
        fromKey = os.path.basename(fromFileFmt)

        ff = os.listdir(fromPath)
        for f in ff:
            fileName = fromPath + os.path.sep + f
            if not os.path.isfile(fileName): continue
            if not fnmatchcase(f, fromKey): continue
            LoggerUtils.println(f)
            shutil.copyfile(fileName, toPath + os.sep + f)

    @staticmethod
    def copyDir(fromDir, toDir, cb=None):
        if not os.path.exists(toDir): os.makedirs(toDir)
        for f in os.listdir(fromDir):
            fromFile = fromDir + os.sep + f
            toFile = toDir + os.sep + f
            if os.path.isdir(fromFile):
                FileUtils.copyDir(fromFile, toFile)
            elif cb is None or cb(fromFile, f):
                shutil.copy(fromFile, toFile)

    @staticmethod
    def remove_tree(path):
        if os.path.isdir(path):
            items = os.listdir(path)
            for item in items:
                full_path = os.path.join(path, item)
                FileUtils.remove_tree(full_path)
            os.rmdir(path)
        else:
            os.remove(path)

    @staticmethod
    def remove(f, rmEmptyDir=True):
        if os.path.isdir(f):
            try:
                FileUtils.remove_tree(f)
            except Exception as e:
                pass
        elif os.path.exists(f):
            try:
                os.remove(f)
                if not rmEmptyDir: return
                pp = os.path.dirname(f)
                while True:
                    os.rmdir(pp)
                    if os.path.exists(pp): break
                    pp = os.path.dirname(pp)
                    if len(pp) <= 1: break
            except Exception as e:
                pass

    @staticmethod
    def sizeToString(size):
        # if 0 < size:
        #     tail = 'PB'
        #     s = '%.02d' % (size / 1024)
        if 109951162776 <= size:
            tail = 'TB'
            s = '%.2f' % (size / 109951162776.00)
        elif 1073741824 <= size:
            tail = 'GB'
            s = '%.2f' % (size / 1073741824.00)
        elif 1048576 <= size:
            tail = 'MB'
            s = '%.2f' % (size / 1048576.00)
        elif 1024 <= size:
            tail = 'KB'
            s = '%.2f' % (size / 1024.00)
        else:
            return '%d B' % (size)
        return s + ' ' + tail  # .strip('0').strip('.')

    START_WITH = 1
    END_WITH = 2
    EQUAL_WITH = 3
    CONTAIN_WITH = 4

    @staticmethod
    def replaceLine(typ, fileName, kv):
        if not os.path.isfile(fileName): return

        # load
        with open(fileName, 'rb') as f: lines = f.readlines()

        newLines = []
        for line in lines:
            l = line.strip()
            for k, v in kv.items():
                if typ == FileUtils.START_WITH:
                    if not l.startswith(k): continue
                    newLines.append(v + '\n')
                    break
                if typ == FileUtils.END_WITH:
                    if not l.endswith(k): continue
                    newLines.append(v + '\n')
                    break
                if typ == FileUtils.EQUAL_WITH:
                    if l != k: continue
                    newLines.append(v + '\n')
                    break
                if typ == FileUtils.CONTAIN_WITH:
                    if l.find(k) < 0: continue
                    newLines.append(v + '\n')
                    break
            else:
                newLines.append(line)
        # save
        with open(fileName, 'wb') as f: f.writelines(newLines)

    @staticmethod
    def listFiles(path):
        for dirpath, dirnames, filenames in os.walk(path): return filenames
        return []

    @staticmethod
    def listAll(path):
        for dirpath, dirnames, filenames in os.walk(path): return dirnames + filenames
        return []

    @staticmethod
    def findLastModifyFile(path, pre=None, tail=None):
        ff = FileUtils.listFiles(path)
        if None == ff: return None
        lastTs = 0
        lastFile = None
        for f in ff:
            if not CmnUtils.isEmpty(pre) and not f.startswith(pre): continue
            if not CmnUtils.isEmpty(tail) and not f.endswith(tail): continue
            ts = FileUtils.getModifyTime(path + os.sep + f)
            if ts < lastTs: continue
            lastTs = ts
            lastFile = path + os.sep + f
        return lastFile

def run():
    print(FileUtils.sizeToString(20))
    print(FileUtils.sizeToString(124))
    print(FileUtils.sizeToString(1025))
    print(FileUtils.sizeToString(1026))
    print(FileUtils.sizeToString(1337))


if __name__ == "__main__":
    run()
