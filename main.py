#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 程序入口
################################################################
from __init__ import debug_flag
from flask_server.server import server


if __name__ == '__main__':
    server.run(port=8001, debug=debug_flag)
