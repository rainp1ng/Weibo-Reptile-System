#!/usr/bin/python
#coding=utf-8
################################################################
# 解析用户微博主页的html内容
# 将内容解析为条为记录的微博内容
# useage:
#   get_weibo_result(user_id)
# return:
#   [...]
################################################################
import sys
import re
import json
import traceback
from HTMLParser import HTMLParser
__author__ = 'rainp1ng'


class WeiboParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.read_flag = False
        self.weibo_list = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for var, val in attrs:
                if var == 'class' and val == 'WB_detail':
                    print var, val
                    self.read_flag = True

    def handle_data(self, data):
        if self.read_flag:
            self.weibo_list.append(data)

    def handle_endtag(self, tag):
        if tag == 'div':
            self.read_flag = False


class ContentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.read_flag = False
        self.other_div = 0
        self.data = []
        self.weibo = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.read_flag:
                self.other_div += 1
                print '+++++++++++++++++++++++++++++++find one start tag , add 1.+++++++++++++++++++++++++++++++++'
                print 'other div:', self.other_div
                for var, val in attrs:
                    if var == 'class':
                        print val
                return
            for var, val in attrs:
                if var == 'class' and val == 'WB_detail':
                    print var, val
                    self.read_flag = True

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.read_flag and self.other_div == 0:
                print 'endtag'
                print self.weibo
                print 'add weibo ... '
                self.data.append(self.weibo)
                self.weibo = []
                self.read_flag = False
            elif self.read_flag:
                self.other_div -= 1
                print '-------------------------------find one end tag , minus 1.---------------------------------'
                print 'other div:', self.other_div

    def handle_data(self, data):
        if self.read_flag:
            content = data.strip()
            if content != '':
                print '*******************************add content ... *********************************************'
                self.weibo.append(content)


def catch_weibo_content(content):
    index_div_start = content.find('<div')
    index_div_end = content.find('</div')
    while index_div_start < index_div_end:
        index_div_start = content.find('<div', index_div_start+len('<div'))
        index_div_end = content.find('</div', index_div_end+len('</div'))
    return index_div_end


def get_weibo_list(crawl_content, key='<div class="WB_detail">'):
    index = crawl_content.find(key)
    weibo_list = []
    while index != -1:
        crawl_content = crawl_content[index+len(key):].strip()
        index_div_end = catch_weibo_content(crawl_content)
        weibo_content = re.sub('<!--[^<>]+>', '', crawl_content[:index_div_end])
        final_content = weibo_content
        weibo_list.append(final_content)
        index = crawl_content.find(key)
    return weibo_list


def save_weibo_list(weibo_list):
    info = '<!doctype html>\n' \
            '<html>\n' \
            '<head>\n' \
            '<meta charset="utf-8">\n'
    for i, weibo_content in enumerate(weibo_list):
        info += '<!--------------------------------%s------------------------------>\n%s\n' % (i, weibo_content)
    return info


def batch_split_weibo_columns(weibo_list):
    return map(split_weibo_columns, weibo_list)


def get_name_and_link(wb_info):
    # 获得发布者昵称和主页链接
    try:
        return re.findall('href=\"([^"]+)\"[^>]+>([\s\S]+?)</a>', wb_info)[0]
    except Exception, e:
        traceback.print_exc()
        try:
            return '', re.findall('class="W_f14 W_fb">([\s\S]+?)</span>', wb_info)[0]
        except Exception, e:
            traceback.print_exc()
            return '', ''


def get_time_and_dev(wb_from):
    # 获取发布时间和发布设备
    try:
        res_dev = re.sub('\s+', ' ', re.sub('</{0,}a[\s\S]{0,}?>', '', wb_from.strip()))
        res_time = re.findall(' title="(\d+-\d+-\d+ \d+:\d+)"\s{0,}date="(\d+)"', wb_from)
        pub_time, unixtime = res_time[0]
        res = re.findall('\d+:\d+\s{0,}([\s\S]+)', res_dev)
        pub_dev = res[0]
        return pub_time, unixtime, pub_dev
    except Exception, e:
        return 'unknown', 'unkown', 'unkown'


def get_text(wb_text):
    # 获得微博主内容(如转发微博，则转发部分的内容)及表情链接、文字链接、视频链接等
    res = re.findall('<a[\s\S]{0,}?href=[\'"]([\s\S]+?)[\'"][\s\S]{0,}?>([\s\S]+?)</a>', wb_text)
    data = {}
    for link, word in res:
        data[word] = link
    res0 = re.sub('</{0,}a[\s\S]{0,}?>', '', wb_text.strip()).strip()
    res1 = re.findall('<img[\s\S]+?src=[\'"]([\s\S]+?)[\'"]', wb_text)
    # res0 为微博正文文字内容, res1 为正文中的图片链接, data为文字对应的链接字典
    return res0, json.dumps(res1), json.dumps(data)


def get_pic(wb_pic):
    # 获得微博中发布者发布的照片链接
    res = re.findall('<img\s{0,}([\s\S]+?)\s{0,}src="([^"]+?)"[\s\S]+?>', wb_pic)
    data_list = []
    for reserved, img_url in res:
        data_list.append(img_url)
    return data_list


def get_video(wb_video):
    return


def split_weibo_columns(weibo):
    # 对单条微博的内容进行解析拆分
    data = {'is_repost': '0'}
    # 获取 WB_info 微博发布者昵称
    wb_info_res = re.findall('<div class="WB_info">([\s\S]+?)</div>', weibo)
    wb_info_list = map(get_name_and_link, wb_info_res)
    data['link'], data['username'] = wb_info_list[0]
    if data['link'] == '':
        return data
    # 获取发布时间与发布设备
    wb_from_res = re.findall('<div class="WB_from S_txt2">([\s\S]+?)</div>', weibo)
    # print '----------------------%s---------------------' % len(wb_info_list)
    wb_from_list = map(get_time_and_dev, wb_from_res)
    data['pub_time'], data['unixtime'], data['pub_dev'] = wb_from_list[0]
    # 获取微博主要内容
    wb_text_res = re.findall('<div class="WB_text\s?\w{0,}?"[\s\S]+?>([\s\S]+?)</div>', weibo)
    wb_text_list = map(get_text, wb_text_res)
    data['content'], data['content_pics'], data['content_link'] = wb_text_list[0]
    # 获取发布者发布的视频预览图、图片链接
    index = weibo.find('<div class="WB_media_wrap clearfix"')
    wb_pic_res = weibo[index + len('<div class="WB_media_wrap clearfix"'):]
    data['pictures'] = json.dumps(get_pic(wb_pic_res))
    # 转发微博类型 内容处理
    if len(wb_info_res) > 1:
        data['is_repost'] = '1'
        data['repost_from_link'], data['repost_from_username'] = wb_info_list[1]
        data['repost_from_pub_time'], data['repost_from_unixtime'], data['repost_from'] = wb_from_list[1]
        # 获取转发微博内容
        data['repost_from_content'], data['repost_from_content_pics'], data['repost_from_content_link'] = wb_text_list[1]
    return data

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    weibo_list = open('../dump_weibo_list.html', 'rb').read()#.read().replace('   ', '')
    import json
    weibo_list = json.loads(weibo_list)
    f = open('test.html', 'wb')
    f.write(save_weibo_list(weibo_list))
    f.close()
    data = batch_split_weibo_columns(weibo_list)
    for i in data:
        for j in i:
            print j, i[j]
        print

