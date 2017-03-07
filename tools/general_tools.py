#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 基本逻辑操作封装
################################################################
import sys
import time
import gzip
import random
from __init__ import debug_flag
from StringIO import StringIO

reload(sys)
sys.setdefaultencoding('utf-8')


def get_random_digit():
    return int(random.random()*100 % 9)


def generate_unix_timestamp(digit_num=12):
    ts = str(time.time()).replace('.', '')
    for i in range(digit_num-12):
        ts += str(get_random_digit())
    return ts


def gunzip(content):
    return gzip.GzipFile(fileobj=StringIO(content)).read()


if __name__ == '__main__':
    print
