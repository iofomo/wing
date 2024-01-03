#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for zip/unzip file
# @date:   2023.08.10 14:40:50

import sys, os, zipfile, time, shutil
from utils.utils_import import ImportUtils
from utils.utils_logger import LoggerUtils

ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
class ZipUtils:

    @staticmethod
    def readFile(zipFile, oldFileName, desFile):
        z = zipfile.ZipFile(zipFile, 'r')
        for name in z.namelist():
            if name.endswith('/'): continue
            if name != oldFileName: continue
            with open(desFile, 'w+b') as f:
                f.write(z.read(name))
            break
        z.close()

    @staticmethod
    def readContent(zipFile, fileName):
        c = None
        z = zipfile.ZipFile(zipFile, 'r')
        for name in z.namelist():
            if name.endswith('/'): continue
            if name != fileName: continue
            c = z.read(name)
            break
        z.close()
        return c

    # files: { "zip file name" : "new file"}
    @staticmethod
    def insertFiles(zipFile, files):
        ZipUtils.removeFiles(zipFile, files.keys())
        z = zipfile.ZipFile(zipFile, 'a')
        for oldFile, newFile in files.items():
            z.write(newFile, oldFile)
        z.close()

    @staticmethod
    def removeFiles(zipFile, oldFiles):
        tmpZipFile = '%s_%d' % (zipFile, int(time.time()))
        zin = zipfile.ZipFile(zipFile, 'r')
        zout = zipfile.ZipFile(tmpZipFile, 'w')
        for item in zin.infolist():
            if item.filename in oldFiles: continue
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)
        zout.close()
        zin.close()
        shutil.move(tmpZipFile, zipFile)

    @staticmethod
    def newZipAddFiles(zipFilePath, filesList):
        try:
            os.remove(zipFilePath)
        except: pass
        z = zipfile.ZipFile(zipFilePath, 'a')
        for fileSon in filesList:
            LoggerUtils.println(fileSon)
            fileSonName = os.path.basename(fileSon)
            if os.path.isdir(fileSon):
                sons = os.listdir(fileSon)
                for son in sons:
                    z.write(fileSon + os.sep + son, arcname=fileSonName + os.sep + os.path.basename(son))
            z.write(fileSon, arcname=fileSonName)
        z.close()

    @staticmethod
    def isFile(zipFile, oldFileName):
        ret = False
        z = zipfile.ZipFile(zipFile, 'r')
        for name in z.namelist():
            if name.endswith('/'): continue
            if name != oldFileName: continue
            ret = True
            break
        z.close()
        return ret

    @staticmethod
    def isContainsFile(zipFile, endsName):
        ret = False
        z = zipfile.ZipFile(zipFile, 'r')
        for name in z.namelist():
            if not name.endswith(endsName): continue
            ret = True
            break
        z.close()
        return ret

    @staticmethod
    def zipDir(inPath, outZipFile, ignoreDirs=['__MACOSX'], ignoreFiles=['.DS_Store']):
        ZipUtils.zipDir2(inPath, outZipFile, False, ignoreDirs, ignoreFiles)

    @staticmethod
    def zipDir2(inPath, outZipFile, ownDir, ignoreDirs=['__MACOSX'], ignoreFiles=['.DS_Store']):
        l = len(os.path.dirname(inPath) if ownDir else inPath) + 1
        zf = zipfile.ZipFile(outZipFile, "w", zipfile.zlib.DEFLATED)
        ss = set()
        if os.path.isfile(inPath):
            zf.write(inPath, inPath[l:])
        else:
            for root, dirs, files in os.walk(inPath):
                if ignoreDirs is not None:
                    rname = os.path.basename(root)
                    if rname in ignoreDirs: continue
                for name in files:
                    if ignoreFiles is not None and name in ignoreFiles: continue
                    pp = root[l:]
                    if pp not in ss:
                        ss.add(pp)
                        zf.write(root, pp)
                    f = os.path.join(root, name)
                    zf.write(f, f[l:])
        zf.close()

    @staticmethod
    def zipDirWithCallback(inPath, outZipFile, fileCallback=None):
        """
        def fileCallback(fileName, shortFileName):
            # @param fileName: 'name/xxx.log'
            # @param shortFileName: 'xxx.log'
            pass
        """
        return ZipUtils.zipDirWithCallback2(inPath, outZipFile, False, fileCallback)

    @staticmethod
    def zipDirWithCallback2(inPath, outZipFile, ownDir, fileCallback=None):
        fcnt = 0
        l = len(os.path.dirname(inPath) if ownDir else inPath) + 1
        zf = zipfile.ZipFile(outZipFile, "w", zipfile.ZIP_DEFLATED)
        ss = set()
        if os.path.isfile(inPath):
            fcnt += 1
            zf.write(inPath, inPath[l:])
        else:
            for root, dirs, files in os.walk(inPath):
                for name in files:
                    f = os.path.join(root, name)
                    pp = root[l:]
                    if fileCallback is not None and fileCallback(pp, name): continue
                    if pp not in ss:
                        ss.add(pp)
                        zf.write(root, pp)
                    zf.write(f, f[l:])
                    fcnt += 1
        zf.close()
        return fcnt

    @staticmethod
    def unzip(inZipFile, outPath, cb=None):
        if not os.path.isdir(outPath): os.makedirs(outPath)
        zfile = zipfile.ZipFile(inZipFile, 'r')
        for fileName in zfile.namelist():
            zfile.extract(fileName, outPath)
            if fileName.endswith('/'): continue
            if cb is None: continue
            fullName = os.path.normpath(os.path.join(outPath, fileName))
            cb(fullName)
        zfile.close()

    @staticmethod
    def unzip2(inZipFile, outPath, cb):
        if not os.path.isdir(outPath): os.makedirs(outPath)
        zfile = zipfile.ZipFile(inZipFile, 'r')
        for fileName in zfile.namelist():
            if fileName.endswith('/'): continue
            fullName = os.path.normpath(os.path.join(outPath, fileName))
            ret = cb(fullName, fileName)
            if ret < 0: break
            if 0 == ret: continue
            zfile.extract(fileName, outPath)
        zfile.close()

    @staticmethod
    def zipFile(inFile, outZipFile, adbname=None):
        f = zipfile.ZipFile(outZipFile, 'w', zipfile.ZIP_DEFLATED)
        f.write(inFile, os.path.basename(inFile) if adbname is None else adbname)
        f.close()

    @staticmethod
    def zipFiles(inFiles, outZipFile):
        f = zipfile.ZipFile(outZipFile, 'w', zipfile.ZIP_DEFLATED)
        for inFile in inFiles:
            f.write(inFile, os.path.basename(inFile))
        f.close()

    @staticmethod
    def parseFiles(zipFile, sw=None):
        ff = []
        z = zipfile.ZipFile(zipFile, 'r')
        for name in z.namelist():
            if name.endswith('/'): continue
            if sw is not None:
                if name.startswith(sw): ff.append(name)
                continue
            ff.append(name)
        z.close()
        return ff

    @staticmethod
    def parseNames(zipFile):
        ff = list()
        z = zipfile.ZipFile(zipFile, 'r')
        for f in z.namelist():
            if not f.endswith('/'): ff.append(f)
        z.close()
        return ff

    @staticmethod
    def unzipSub(inZipFile, zFileName, desPath):
        if not os.path.isdir(desPath):
            os.makedirs(desPath)
        zfile = zipfile.ZipFile(inZipFile, 'r')
        for fileName in zfile.namelist():
            if fileName != zFileName: continue
            zfile.extract(fileName, desPath)
            break
        zfile.close()

    @staticmethod
    def isZipFile(fileName):
        if not fileName: return False
        return zipfile.is_zipfile(fileName)
