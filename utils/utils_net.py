#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for network
# @date:   2023.09.10 14:40:50

import sys, os, tempfile, subprocess
from utils.utils_cmn import CmnUtils

try:
    from urllib import request as url_request
except ImportError:
    import urllib2 as url_request

from utils.utils_cmn import CmnUtils


# -------------------------------------------------------------
class NetUtils:

    @staticmethod
    def isConnectable(url):
        try:
            res = url_request.urlopen(url)
            return res.getcode() == 200
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def __convert__(s):
        try:
            return s.decode()
        except Exception as e:
            print(e)
            return s

    @staticmethod
    def downloadContentByWeb(url, header=None):
        try:
            if None == header and not CmnUtils.isOsWindows():
                _out, _err = CmnUtils.doCmdEx('curl ' + url)
                if None != _out: return NetUtils.__convert__(_out)
                print('curl fail')

            nullProxyHandler = url_request.ProxyHandler({})
            opener = url_request.build_opener(nullProxyHandler)
            if None == header:
                opener.addheaders = [('User-agent',
                                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
                                      )]
            else:
                opener.addheaders = header
            response = opener.open(url)
            return NetUtils.__convert__(response.read())
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def downloadContent(url):
        try:
            if not CmnUtils.isOsWindows():
                _out, _err = CmnUtils.doCmdEx('curl ' + url)
                if None != _out: return NetUtils.__convert__(_out)
                print('curl fail')

            f = url_request.urlopen(url)
            return NetUtils.__convert__(f.read())
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def downloadFile(url, f):
        if os.path.exists(f): os.remove(f)
        try:
            if not CmnUtils.isOsWindows():
                CmnUtils.doCmdEx('curl ' + url + ' > ' + f)
                if os.path.isfile(f): return True
                print('curl fail')

            net = url_request.urlopen(url)
            with open(f, "wb") as ff:
                ff.write(net.read())
            return os.path.isfile(f)
        except Exception as e:
            print(e)
        if os.path.exists(f): os.remove(f)
        return False

    @staticmethod
    def downloadFileWithProgress(url, dldFile):
        response = url_request.urlopen(url)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 10240

        with open(dldFile, 'wb') as file:
            lastMsg = None
            downloaded_size = 0
            while True:
                buffer = response.read(block_size)
                if not buffer: break

                downloaded_size += len(buffer)
                file.write(buffer)

                progress = int(50 * downloaded_size / total_size)
                msg = "[%s%s] %d%%" % ('=' * progress, ' ' * (50 - progress), 2 * progress)
                if lastMsg == msg: continue
                lastMsg = msg
                sys.stdout.write(msg)
                sys.stdout.write('\n')
                sys.stdout.flush()

    @staticmethod
    def downloadFileByWeb(url, f):
        if os.path.exists(f): os.remove(f)
        try:
            nullProxyHandler = url_request.ProxyHandler({})
            opener = url_request.build_opener(nullProxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            response = opener.open(url)
            with open(f, "wb") as content:
                content.write(response.read())
            return os.path.isfile(f)
        except Exception as e:
            print(e)
        if os.path.exists(f): os.remove(f)
        return False
