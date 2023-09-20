#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: publish module to maven
# @date:   2023.05.10 14:40:50

import sys, os, time
from datetime import datetime, timedelta
g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_file import FileUtils
from utils.utils_logger import LoggerUtils
from utils.utils_properties import PropertiesUtils
from utils.utils_import import ImportUtils
from basic.repoin import BasicRepoIn
from basic.xmlreader import BasicXmlReader
from basic.resource import Resource

g_env_path, g_this_file, g_this_path = ImportUtils.initEnv()
g_repo_path = ImportUtils.initPath(g_env_path)
# --------------------------------------------------------------------------------------------------------------------------
class DocumentCollector:
    def __init__(self, usr):
        self.usr = usr
        self.today, self.lastday = None, None
        self.cacher = []

    def doCollect(self):
        fsrc = open(g_repo_path + '/doc.md', 'wb')
        self.__doCollectDoc__(fsrc)
        self.__doCollectPlatformDoc__(fsrc)
        self.__doCollectModuleDoc__(fsrc)
        fsrc.close()

    def __doCollectDoc__(self, fsrc):
        path = g_repo_path + '/doc'
        if not os.path.isdir(path): return
        LoggerUtils.light('refresh: doc ...')

        '''
        # 开发组文档（doc）
        
        >   [开发设计文档](demo/开发设计.pdf)
        >   最近更新： xxx <xxx>（2023-05-27 18:36:39）
        '''
        self.__doCollectPath__(path)
        self.cacheFlush(fsrc, Resource.getString(0) + '\n\n')

    def __do_write__(self, f, l): f.write(l.encode())

    def cacheReset(self): self.cacher = []
    def cacheAppend(self, line): self.cacher.append(line)
    def cacheFlush(self, fsrc, tag1=None, tag2=None, tag3=None):
        if len(self.cacher) <= 0: return # empty
        if tag1 != None: self.__do_write__(fsrc, tag1)
        if tag2 != None: self.__do_write__(fsrc, tag2)
        if tag3 != None: self.__do_write__(fsrc, tag3)
        for line in self.cacher: self.__do_write__(fsrc, line)
        self.cacheReset()

    def __doCollectPlatformDoc__(self, fsrc):
        path = g_repo_path + '/platform/doc'
        if not os.path.isdir(path): return
        LoggerUtils.light('refresh: platform/doc ...')

        '''
        # 平台组文档（doc）
        
        >   [开发设计文档](demo/开发设计.pdf)
        >   最近更新： xxx <xxx>（2023-05-27 18:36:39）
        '''
        self.__doCollectPath__(path)
        self.cacheFlush(fsrc, Resource.getString(1) + '\n\n')

    def checkExt(self, f):
        ext = FileUtils.getFileExt(f)
        if ext == '.md': return 100 < os.path.getsize(f)
        if ext not in ['.pdf','.doc','.docx']: return False
        return not os.path.isfile(f[:-len(ext)] + '.md')

    def __doCollectPath__(self, path):
        self.cacheReset()
        for root, dirs, files in os.walk(path):
            for f in files:
                filename = os.path.join(root, f)
                if os.path.basename(os.path.dirname(filename)).endswith('.assets'): continue
                if not self.checkExt(filename): continue
                self.__doCollectItem__(path, filename[len(path)+1:])

    def __doCollectModuleDoc__(self, fsrc):
        LoggerUtils.light('refresh: module/doc ...')
        self.__do_write__(fsrc, Resource.getString(2) + '\n\n')

        '''
        # 模块组文档
        
        >   [开发设计文档](demo/开发设计.pdf)
        >   最近更新： xxx（2023-05-27 18:36:39）
        '''
        def scanPath(path, level, dirs):
            #获取该目录下所有的文件名称和目录名称
            ll = os.listdir(path)
            for l in ll:
                if l.startswith('.'): continue
                d = path + os.sep + l
                if not os.path.isdir(d): continue
                if l == 'doc':
                    dirs.append(d)
                    continue
                if 3 < level: continue
                scanPath(d, level + 1, dirs)

        dirs = []
        scanPath(g_repo_path, 1, dirs)
        lastPath = ''
        for dir in dirs:
            path = dir[len(g_repo_path)+1:]
            if path in ['doc','platform/doc','platform\\doc']: continue
            if path.startswith('platform/template'): continue
            pos = path.find('/')
            if pos < 0: pos = path.find('\\')
            if pos < 0: continue
            self.__doCollectPath__(dir)
            if len(self.cacher) <= 0: continue
            pname = path[:pos]
            if lastPath != pname:
                lastPath = pname
                fsrc.write(('### ' + pname + '\n').encode())
            self.cacheFlush(fsrc, '-   #### ' + os.path.dirname(path[pos+1:]) + '\n')

    def isNewest(self, ss):
        s = '%s' % ss
        if None == self.today:
            # d = datetime.date.today()
            # self.today = "%d-%02d-%02d" % (d.year, d.month, d.day)
            self.today = datetime.now().strftime('%Y-%m-%d')
        if None == self.lastday:
            # d = datetime.date.today() - datetime.timedelta(days=2)
            # self.lastday = "%d-%02d-%02d" % (d.year, d.month, d.day)
            self.lastday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

        if s.startswith(self.today): return True
        if s.startswith(self.lastday): return True
        return False

    def __doCollectItem__(self, fpath, fname):
        ret = CmnUtils.doCmd('cd %s && git log -1 %s' % (fpath, fname))
        author = self.usr
        if None == ret or ret.find('Author:') < 0:
            timeArray = time.localtime(os.path.getmtime(fpath + os.sep + fname))
            date = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        else:
            items = ret.split('\n')
            for item in items:
                item = item.strip()
                if item.startswith('Author:'):
                    author = item[len('Author:'):].strip()
                    pos = author.find('<')
                    if 0 < pos: author = author[:pos].strip()
                elif item.startswith('Date:'):
                    tmp = item[len('Date:'):].strip().split(' ')[:5]
                    date = datetime.strptime(' '.join(tmp),'%a %b %d %H:%M:%S %Y')
        self.__doWriteItem__(fpath + os.sep + fname, author, date)

    def __doWriteItem__(self, fname, author, date):
        title = None
        if fname.endswith('.md'):
            with open(fname, 'rb') as f:
                while True:
                    line = f.readline().decode()
                    if len(line) <= 0: break
                    if not line.startswith('#'): continue
                    title = line.strip('#')
                    break
        if None == title or len(title) <= 0:
            title = os.path.basename(fname)
            pos = title.rfind('.')
            if 0 < pos: title = title[:pos]

        '''
        
        >   [开发设计文档](demo/开发设计.pdf) 
        >   最近更新：xxx <xxx>（2023-05-27 18:36:39）
        '''
        self.cacheAppend('>   [%s](%s)\n' % (title.strip(), fname[len(g_repo_path)+1:]))
        if self.isNewest(date):
            self.cacheAppend((Resource.getString(3) + '\n') % (author, date))
        else:
            self.cacheAppend((Resource.getString(4) + '\n') % (author, date))
        self.cacheAppend('\n')

def doRefreshPermit():
    # add x right to the file
    LoggerUtils.light('refresh: *.sh, gradlew rights ...')
    def scanPath(path, level):
        #获取该目录下所有的文件名称和目录名称
        ll = os.listdir(path)
        for l in ll:
            if l.startswith('.'): continue
            d = path + os.sep + l
            if os.path.isdir(d):
                if level <= 4: scanPath(d, level + 1)
                continue
            if l.endswith('.sh') or l in ['gradlew']:
                CmnUtils.doCmd('chmod a+x ' + d)
                continue

    scanPath(g_repo_path, 1)

def doRefreshGradle():
    gf = g_repo_path + '/default.gradle'
    if not os.path.isfile(gf): return

    LoggerUtils.light('refresh: default.gradle ...')
    mvnusr = PropertiesUtils.get(g_repo_path + '/.repo/repo.properties', 'mvnusr')
    mvnpwd = PropertiesUtils.get(g_repo_path + '/.repo/repo.properties', 'mvnpwd')
    if CmnUtils.isEmpty(mvnusr) or CmnUtils.isEmpty(mvnpwd):
        LoggerUtils.w('No mvn account found !')
        return
    with open(gf, 'r') as f: lines = f.readlines()

    updated = False
    newLines = []
    kusr, kpwd = '---usr---', '---pwd---'
    for line in lines:
        pos = line.find(kusr)
        if 0 < pos:
            updated = True
            newLines.append(line[:pos] + mvnusr + line[pos + len(kusr):])
            continue
        pos = line.find(kpwd)
        if 0 < pos:
            updated = True
            newLines.append(line[:pos] + mvnpwd + line[pos + len(kpwd):])
            continue
        newLines.append(line)
    if not updated: return
    with open(gf, 'w') as f: f.writelines(newLines)

def isValidCMakelists(makeFile):
    with open(makeFile, 'r') as f: lines = f.readlines()
    for line in lines:
        line = line.strip()#project(ifma_
        # if line.startswith('project') and line.find('ifma_') < 0: return False
        if line.startswith('add_subdirectory'): return False
        if line.startswith('include_directories'): return True
    return False

CMAKELIST_LEVEL_MAX = 6
def doScanCMakeLists(path, ignoreDirs, outFiles, level=0):
    level += 1
    for fname in os.listdir(path):
        f = os.path.join(path, fname)
        if os.path.isdir(f):
            if CMAKELIST_LEVEL_MAX < level: continue
            if fname.startswith('.'): continue
            if fname not in ignoreDirs: doScanCMakeLists(f, ignoreDirs, outFiles, level)
            continue
        if fname != 'CMakeLists.txt': continue
        if not isValidCMakelists(f): continue
        fname = os.path.dirname(f)[len(g_repo_path)+1:]
        if CmnUtils.isEmpty(fname): continue
        outFiles.append(fname)

def doFixCMakelist(mf):
    mlFile = g_repo_path + '/CMakeLists.txt'
    if not os.path.exists(mlFile): return
    cname = BasicXmlReader.readAttributeByElementIndex(mf, "meta-data", 0, "cmake")
    cplatform = BasicXmlReader.readAttributeByElementIndex(mf, "meta-data", 0, "platform")
    if CmnUtils.isEmpty(cname) or CmnUtils.isEmpty(cplatform): return
    LoggerUtils.light('refresh: CMakeLists.txt ' + cname)

    if 'android' != cplatform: return # only for Android
    if 'ANDROID_HOME' not in os.environ: return # make sure env right

    # load
    with open(mlFile, 'r') as f: lines = f.readlines()
    # search include_directories
    for line in lines:
        line = line.strip()
        if line.startswith('include_directories'): return # has fixed
        if line.startswith('project(') and line.find('ifma') < 0: return # local not for Android

    # fix
    needFixed = True
    with open(mlFile, 'w') as f:
        for line in lines:
            f.write(line)
            l = line.strip()
            if needFixed and l.startswith('project'):
                sdkPath = os.environ['ANDROID_HOME']
                f.writelines('\n')
                f.writelines('# system include\n')
                f.writelines('include_directories(%s/ndk/21.4.7075529/sysroot/usr/include)\n' % sdkPath)
                f.writelines('include_directories(%s/ndk/21.4.7075529/sources/android/support/include)\n' % sdkPath)
                needFixed = False

def doRefreshCMakelist(mf):
    cname = BasicXmlReader.readAttributeByElementIndex(mf, "meta-data", 0, "cmake")
    if CmnUtils.isEmpty(cname): return
    LoggerUtils.light('refresh: CMakeLists.txt ' + cname)

    isAndroid = cname.endswith('a')

    # scan
    outFiles = []
    doScanCMakeLists(g_repo_path, ['build','lib','libs','src','inc','main'], outFiles)

    # update root CMakeLists.txt
    with open(g_repo_path + '/CMakeLists.txt', 'w') as f:
        f.write('cmake_minimum_required(VERSION 3.6.0)\n')
        f.write('project(%s)\n\n' % (cname))

        if isAndroid and 'ANDROID_HOME' in os.environ:
            sdkPath = os.environ['ANDROID_HOME']
            f.writelines('# system include\n')
            f.writelines('include_directories(%s/ndk/21.4.7075529/sysroot/usr/include)\n' % sdkPath)
            f.writelines('include_directories(%s/ndk/21.4.7075529/sources/android/support/include)\n' % sdkPath)

        lastSubGroup = None
        for outFile in outFiles:
            pos1 = outFile.find('/')
            pos2 = outFile.find('\\')
            if 0 < pos1 or 0 < pos2:
                if pos1 <= 0: pos1 = pos2
                if pos2 <= 0: pos2 = pos1
                pos = pos1 if pos1 < pos2 else pos2
                subGroup = outFile[:pos]
            else:
                subGroup = outFile
            if subGroup != lastSubGroup:
                lastSubGroup = subGroup
                f.writelines('\n# %s\n' % subGroup)
                LoggerUtils.light(subGroup)

            if not isAndroid and outFile.endswith('ifma'): continue
            LoggerUtils.println('add: ' + outFile)
            f.writelines('add_subdirectory(%s)\n' % outFile)

def run():
    '''
    repo -refresh
    '''
    repo = BasicRepoIn(g_repo_path)
    repo.println()

    doRefreshPermit()
    doRefreshGradle()
    doFixCMakelist(repo.getManifestFile())
    # doRefreshCMakelist(repo.getManifestFile())
    DocumentCollector(repo.getName()).doCollect()

if __name__ == "__main__":
    run()