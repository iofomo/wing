#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  load resource
# @date:   2023.05.10 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils


# ----------------------------------------------------------------------------------------------------------------------
class Resource:
    sRes = None

    @classmethod
    def __do_init__(cls):
        cls.sRes = {}
        path = os.path.dirname(g_this_path)
        f = path + 'res/res-' + CmnUtils.getLanguageName() + '.txt'
        with open(f, 'rb') as f:
            while True:
                line = f.readline().decode()
                if CmnUtils.isEmpty(line): break
                pos = line.find('=')
                if pos <= 0: continue
                k = line[:pos].strip()
                if CmnUtils.isEmpty(k): continue
                v = line[pos + 1:].strip()
                if len(v) < 2: continue
                cls.sRes[k] = v[1:-1]
        # print(cls.sRes)

    @classmethod
    def getString(cls, typ):
        if None == cls.sRes: cls.__do_init__()
        k = '%d' % typ
        return cls.sRes[k] if k in cls.sRes else ''

# if __name__ == "__main__":
#    Resource.getString(0)
