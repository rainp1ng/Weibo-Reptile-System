#!/usr/bin/python
#coding=utf-8
################################################################
# 解析搜索用户界面的html内容
################################################################
from HTMLParser import HTMLParser
__author__ = 'rainp1ng'


class UserHTMLParser(HTMLParser):
    # 解析搜索结果返回的html，最终获得搜索用户的结果html
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []
        self.read_flag = False
        self.user_list_html = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.read_flag = True
            self.data.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'script':
            self.read_flag = False

    def handle_data(self, data):
        if self.read_flag:
            if 'pl_user_feedList' in data:
                # self.user_list_str = data.split('.pageletM.view')[1]
                self.user_list_html = eval(data.split('.pageletM.view')[1])['html'].replace('\\/', '/')


class UserParser(HTMLParser):
    # 对获取的搜索用户结果进行解析的parser类
    def __init__(self):
        HTMLParser.__init__(self)
        self.user_list = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attr, value) in attrs:
                if attr == 'class' and value == 'W_texta W_fb':
                    self.user_list.append(attrs)


if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from http_tools import WeiboHandler
    wh = WeiboHandler('527868739@qq.com', '201314')
    for i in wh.get_user_list('王思聪'):
        print i
        print i['title'], ':', i['user_id']
        print i
