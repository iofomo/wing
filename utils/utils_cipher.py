#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for data or file cipher
# @date:   2023.08.10 14:40:50

import os, sys, hashlib


# --------------------------------------------------------------------------------------------------------------------
class CipherUtils:

    @staticmethod
    def md5hex(word):
        """
        MD5加密算法，返回32位小写16进制符号
        """
        if isinstance(word, unicode):
            word = word.encode("utf-8")
        elif not isinstance(word, str):
            word = str(word)
        m = hashlib.md5()
        m.update(word)
        return m.hexdigest()

    @staticmethod
    def md5File(fname):
        """
        计算文件的MD5值
        """

        def read_chunks(fh):
            fh.seek(0)
            chunk = fh.read(8096)
            while chunk:
                yield chunk
                chunk = fh.read(8096)
            else:  # 最后要将游标放回文件开头
                fh.seek(0)

        m = hashlib.md5()
        if isinstance(fname, basestring) \
                and os.path.exists(fname):
            with open(fname, "rb") as fh:
                for chunk in read_chunks(fh):
                    m.update(chunk)
                    # 上传的文件缓存 或 已打开的文件流
        elif fname.__class__.__name__ in ["StringIO", "StringO"] \
                or isinstance(fname, file):
            for chunk in read_chunks(fname):
                m.update(chunk)
        else:
            return ""
        return m.hexdigest().lower()

    @staticmethod
    def md5String(s):
        md5_obj = hashlib.md5()
        md5_obj.update(s.encode('utf-8'))
        hash_code = md5_obj.hexdigest()
        return hash_code

    @staticmethod
    def sha256File(file_path):
        with open(file_path, 'rb') as f:
            sha256_obj = hashlib.sha256()
            while True:
                data = f.read(4096)
                if not data:
                    break
                sha256_obj.update(data)
            hash_code = sha256_obj.hexdigest()
            return hash_code

    @staticmethod
    def sha256String(s):
        sha256_obj = hashlib.sha256()
        sha256_obj.update(s.encode('utf-8'))
        hash_code = sha256_obj.hexdigest()
        return hash_code

    @staticmethod
    def getUnique(v):
        """
        like with: c/java/python
        :param v: string
        :return:
        """
        l = len(v)
        if l <= 0: return 0, 0
        f = ord(v[0]) | (ord(v[l >> 1]) << 6) | (ord(v[l - 1]) << 12) | (l << 20);

        h = 0
        for i in range(l):
            h = (h << 4) + ord(v[i]);
            g = h & 0xf0000000;
            h ^= g;
            h ^= g >> 24;
        return h, f
