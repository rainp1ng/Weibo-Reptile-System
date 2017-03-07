#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 操作微博的类WeiboHandler
# 模拟登陆微博及请求微博各个操作的函数
# useage:
#   wh = WeiboHandler(username, passwd)
# functions:
# 1.获得搜索的用户名及其用户id
# useage:
#   wh.get_search_result(username)
# return:
#   [{'title':title,'href':href,'user_id':user_id},...]
# 2.
################################################################
import re
import os
import sys
import rsa
import json
import base64
import urllib
import random
import urllib2
import binascii
import urlparse
import cookielib
import traceback
from general_tools import generate_unix_timestamp, gunzip
from html_parser.user_search_parser import UserHTMLParser, UserParser
from html_parser.user_weibo_parser import get_weibo_list, batch_split_weibo_columns
from __init__ import debug_flag
__author__ = 'rainp1ng'
html_files = 'html_files'
json_files = 'json_files'
conf = {
    'slash': '\\',
    'root_path': '',
    'rm_cmd': 'del',
    'mkdir_cmd': 'md'
}
os.system('%(mkdir_cmd)s cookies' % conf)


def get_random_digit():
    return int(random.random()*100 % 9)


class Response(object):
    def __init__(self, content):
        self.message = content

    def read(self):
        return self.message


class WeiboHandler(object):
    def __init__(self, username, passwd, png_path=''):
        self.user = username
        self.passwd = passwd
        self.log_flag = False
        self.domain = 100306
        self.cookie_flag = False
        self.cj = self.set_cookie()
        self.conn = self.set_conn()
        self.fail_error = ''
        self.png_path = png_path

    def set_agent(self, headers):
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
        return headers

    def set_conn(self):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        return urllib2

    def set_cookie(self):
        cookie_name = '%(root_path)scookies%(slash)s' % conf + str(self.user) + '.cookie'
        print "cookie_name:", cookie_name
        if os.path.exists(cookie_name):
            cj = cookielib.LWPCookieJar(cookie_name)
            cj.load(cookie_name, ignore_discard=True, ignore_expires=True)
            self.log_flag = True
            self.cookie_flag = True
        else:
            cj = cookielib.LWPCookieJar(cookie_name)
            self.log_flag = False
            self.cookie_flag = False
        return cj

    def save_cookie(self):
        self.cj.save(ignore_discard=True, ignore_expires=True)

    def check_log_status(self, content):
        print "========================= check log status ========================="
        if debug_flag:
            print 'check_log_status:', content
        if ('登录' in content and '注册' in content) or 'Running out time !' in content:
            # cookie无效
            self.log_flag = False
            os.system('%(rm_cmd)s %(root_path)scookies%(slash)s' % conf + self.user+'.cookie')
            self.set_cookie()
            self.set_conn()
        else:
            self.log_flag = True
        print 'log status:', self.log_flag
        return self.log_flag

    def get_cookie_homepage(self):
        cookie = "SUB=_2AkMhvLiNf8NjqwJRmP0Vy2jnbYx1zwnEiebDAHzsJxJjHiFO7DxnqJeFFSVM_sSebtWH5dL8wgsDH4NE; " \
                 "SUBP=0033WrSXqPxfM72-Ws9jqgMF55z29P9D9WF5DK_WgU-shbixmGYFavoa; " \
                 "SINAGLOBAL=6955529041275.635.1458484024618; " \
                 "ULV=1458484024670:1:1:1:6955529041275.635.1458484024618:"
        return cookie

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
            "Host": "weibo.com",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
        }

    def get_vercode(self):
        self.prelog_data['digits'] = int(random.random() * 1e8)
        url = 'http://login.sina.com.cn/cgi/pin.php?r=%(digits)s&s=0&p=%(pcid)s' % self.prelog_data
        content = self.get(url).read()
        no = str(int(random.random()*100000))
        write_file(self.png_path + 'vercode%s.png' % no, content, True)
        print 'vercode%s.png' % no
        return no

    def set_vercode(self):
        self.get_vercode()
        return raw_input('verification code:').strip()

    def access_vercode(self):
        vercode = self.set_vercode()
        pcid = self.prelog_data['pcid']
        return vercode, pcid

    def log_in_step_1(self, vercode=''):
        login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': '',
            'pcid': '',
            'door': '',
            'vsnf': '1',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'rsakv': '',
            'sp': '',
            'sr': '',
            'encoding': 'UTF-8',
            'prelt': '115',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        data['su'] = get_username(self.user)
        data['servertime'] = self.prelog_data['servertime']
        data['rsakv'] = self.prelog_data['rsakv']
        data['nonce'] = self.prelog_data['nonce']
        data['sp'] = get_passwd(self.prelog_data, self.passwd)
        data['sr'] = '1920*1080'
        data['door'] = vercode
        data['pcid'] = self.prelog_data['pcid']
        content = gunzip(self.post(login_url, data).read())
        write_file('log_in_1.html', content)
        return content

    def log_in(self):
        if self.log_flag:
            return

        print 'log in ... '
        self.prelog()
        try:
            if self.prelog_data['showpin'] == 1:
                self.log_in_step_m()
        except Exception, e:
            pass
        self.log_in_step_0()

    def do_log_req(self, vercode):
        content = self.log_in_step_1(vercode)
        # step 2
        replace_url = re.findall("location.replace\([\'\"]+([^\'\"']+)", content)[0]
        data2 = urlparse.parse_qs(urlparse.urlparse(replace_url).query)
        return data2, replace_url

    def final_log_req(self, replace_url):
        #step 3
        content = self.get(replace_url).read()
        write_file('%s/log_in_2.html' % html_files, content, debug_flag)
        print 'Log in success, save cookie ... '
        self.save_cookie()

    def log_in_step_0(self, vercode=''):
        data2, replace_url = self.do_log_req(vercode)
        if int(data2['retcode'][0]) == 0:
            self.final_log_req(replace_url)
        else:
            print 'Log in failed ... retcode:', data2['retcode'][0], ', reason:', data2['reason'][0].decode('gbk')
            self.fail_error = '%s : %s' % (data2['retcode'][0], data2['reason'][0].decode('gbk'))
            self.log_in_step_m()

    def log_in_step_m(self):
        vercode, pcid = self.access_vercode()
        self.log_in_step_0(vercode)

    def open_weibo_page(self):
        url = "http://weibo.com/"
        if not self.cookie_flag:
            content = self.get(url, self.get_cookie_homepage(), try_time=2).read()
        else:
            content = self.get(url, try_time=2).read()
        if content != 'Running out time !':
            content = gunzip(content)
        write_file('%s/open_weibo_page.html' % html_files, content, debug_flag)
        return content

    def post(self, url, data, cookie='', try_time=7, timeout=7):
        if debug_flag:
            print url
        data_urlencode = urllib.urlencode(data)
        headers = self.set_host(self.get_headers(), url)
        if cookie != '':
            headers['Cookie'] = cookie
        success = False
        res = Response("Running out time !")
        c = 0
        while not success and c < try_time:
            try:
                req = self.conn.Request(url, data=data_urlencode, headers=headers)
                res = self.conn.urlopen(req, timeout=timeout)
                success = True
            except Exception, e:
                success = False
                traceback.print_exc()
                c += 1
        return res

    def get(self, url, cookie='', try_time=7, timeout=7):
        if debug_flag:
            print url
        headers = self.set_host(self.get_headers(), url)
        if cookie != '':
            headers['Cookie'] = cookie
        success = False
        res = Response("Running out time !")
        c = 0
        while not success and c < try_time:
            try:
                req = self.conn.Request(url, headers=headers)
                res = self.conn.urlopen(req, timeout=timeout)
                success = True
            except Exception, e:
                success = False
                traceback.print_exc()
                c += 1
        return res

    def set_host(self, headers, url):
        host = re.findall('http://([^/]+)/', url)
        if len(host) > 0:
            headers['Host'] = host[0]
        else:
            headers['Host'] = 'weibo.com'
        return headers

    def prelog(self):
        unixtime = generate_unix_timestamp(13)
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%(user)s&rsakt=mod&client=ssologin.js(v1.4.18)&_=%(unixtime)s'\
              % {'unixtime': unixtime, 'user': get_username(self.user)}
        content = self.get(url).read()
        try:
            result = re.findall('\((.*)\)', content)[0]
            result = json.loads(result)
        except Exception, e:
            content = gunzip(content)
            result = re.findall('\((.*)\)', content)[0]
            result = json.loads(result)
        write_file('%s/prelog.html' % html_files, content, debug_flag)
        self.prelog_data = result
        return self.prelog_data

    def get_user_list(self, username):
        content = self.get_search_html(username)
        write_file('%s/search.html' % html_files, content, debug_flag)
        user_html_parser = UserHTMLParser()
        user_html_parser.feed(content)
        write_file('%s/user_list.html' % html_files, user_html_parser.user_list_html, debug_flag)

        user_parser = UserParser()
        user_parser.feed(user_html_parser.user_list_html)
        # print user_parser.user_list
        user_list = tuple2dict(user_parser.user_list)
        content = json.dumps(user_list)
        if debug_flag:
            write_file('%s/user_list2.json' % json_files, content, debug_flag)
        return user_list

    def get_search_html(self, username):
        # 获取搜索用户名相关的用户信息
        # username为搜索的用户名
        url = 'http://s.weibo.com/user/%s&Refer=SUer_box' % username
        return gunzip(self.get(url).read())

    def access_homepage(self, user_id):
        # 访问该用户id的用户首页
        url = 'http://weibo.com/%s?is_all=1' % user_id
        content = self.get(url).read()
        if debug_flag:
            print content
        if 'div' not in content:
            content = gunzip(content)
        domain_list = re.findall("CONFIG\['domain'\]='(\d+)'", content)
        if len(domain_list) == 1:
            self.domain = domain_list[0]
        write_file('%s/homepage.html' % html_files, content, debug_flag)
        l = re.findall('\.view\((.+)\)</script>', content)
        for n, i in enumerate(l):
            if 'html' in i and 'WB_detail' in i:
                c = json.loads(i)
        return batch_split_weibo_columns(get_weibo_list(c['html'])), c

    def turn_page(self, user, page):
        url = 'http://weibo.com/%(user_id)s?pids=%(domid)s&' \
              'is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%(page)s&' \
              'ajaxpagelet=1&ajaxpagelet_v6=1&__ref=/%(user_id)s&_t=FM_%(unixtime_15)s' % {
            'user_id': user['user_id'],
            'page': page,
            'domid': user['domid'],
            'unixtime_15': generate_unix_timestamp(15)
        }
        content = gunzip(self.get(url).read())
        user['page'] = page
        user['html_files'] = html_files
        write_file(html_files + '/' + ('turn_page_%(user_id)s_%(page)s.html' % user).replace('/', ''), content, debug_flag)
        l = re.findall('\.view\((.+)\)</script>', content)
        for n, i in enumerate(l):
            if debug_flag:
                print i
            if 'html' in i and 'WB_detail' in i:
                c = json.loads(i)
            else:
                c = json.loads(i)
                c['html'] = ''
        return batch_split_weibo_columns(get_weibo_list(c['html'])), c

    def get_more_weibo(self, user, pagebar, page=1):
        url = 'http://weibo.com/p/aj/v6/mblog/mbloglist?' \
              'ajwvr=6&domain=%(domain)s&is_all=1&pagebar=%(pagebar)s&' \
              'pl_name=%(domid)s&id=%(domain)s%(uid)s&' \
              'script_uri=/%(user_id)s&feed_type=0&page=%(page)s&pre_page=%(page)s&' \
              'domain_op=%(domain)s&__rnd=%(unixtime_13)s' % {
            'user_id': user['user_id'],
            'pagebar': pagebar,
            'page': page,
            'uid': user['uid'],
            'domain': self.domain,
            'domid': user['domid'],
            'unixtime_13': generate_unix_timestamp(13)
        }
        content = gunzip(self.get(url).read())
        user['page'] = page
        user['html_files'] = html_files
        write_file(html_files + '/' + ('get_more_weibo_%(user_id)s_%(page)s.html' % user).replace('/', ''), content, debug_flag)
        c = json.loads(content)
        if debug_flag:
            print c
        return batch_split_weibo_columns(get_weibo_list(c['data'])), c


def get_passwd(prelog_data, origin_passwd):
    pubkey = prelog_data['pubkey']
    servertime = prelog_data['servertime']
    nonce = prelog_data['nonce']
    # print pubkey, servertime, nonce
    rsaPublickey = int(pubkey, 16)
    # print 'rsaPublickey:', rsaPublickey
    key = rsa.PublicKey(rsaPublickey, 65537)
    # print 'key:', key
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(origin_passwd)
    # print 'message:', message
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    return passwd


def get_username(origin_username):
    username = urllib.quote(origin_username)
    username = base64.encodestring(username)[:-1]
    return username


def tuple2dict(data):
    # 把包含二元元组的list转为字典形式
    # data为存储一系列二元元组list转为字典
    new_data = []
    for d in data:
        new_dict = {}
        for attr, value in d:
            new_dict[attr] = value.decode("unicode-escape")
        new_dict['user_id'] = new_dict['href'].split('com/')[1].split('?')[0]
        # print new_dict
        new_data.append(new_dict)
    return new_data


def write_file(filename, content, debug_flag=False):
    if debug_flag:
        file = open(filename, 'wb')
        file.write(content)
        file.close()




