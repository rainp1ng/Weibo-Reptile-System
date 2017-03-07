#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 爬虫逻辑操作封装
################################################################
import sys
import json
import time
import random
from __init__ import debug_flag
from http_tools import WeiboHandler, write_file, json_files
from db_operation.db_tools import *


def generate_user_list_info(user_list):
    user_list_tip = ''
    for i, user in enumerate(user_list):
        user_list_tip += '%s.%s' % (i, user['title'])
    return user_list_tip


def load_more_weibo_info(wh, user, page, pagebar, scrap_id):
    weibo_list, script = wh.get_more_weibo(user, page=page, pagebar=pagebar)
    put_scrap_info(scrap_id, wh.user, user['user_id'], '抓取第%s页第%s部分的%s条微博...' % (page, pagebar + 2, len(weibo_list)))
    write_file('%s/dump_weibo_list_new_%s_%s.json' % (json_files, page, pagebar), json.dumps(weibo_list), debug_flag)
    pagebar += 1
    return weibo_list, script, page, pagebar


def load_turn_page_weibo_info(wh, user, page, pagebar, scrap_id):
    weibo_list, script = wh.turn_page(user, page+1)
    user['domid'] = script['domid']
    user['ns'] = script['ns']
    put_scrap_info(scrap_id, wh.user, user['user_id'], '抓取第%s页第1部分的%s条微博...' % (page + 1, len(weibo_list)))
    write_file('%s/dump_weibo_list_new_%s_00.json' % (json_files, page+1), json.dumps(weibo_list), debug_flag)
    page += 1
    pagebar = 0
    return weibo_list, script, page, pagebar


def log_in(username, passwd):
    wh = WeiboHandler(username, passwd)
    if not wh.log_flag:
        wh.log_in()
    return wh


def scrap_user(wh, user, scrap_id=1111, sleep_gap=5):
    # time.sleep(int(random.random() * sleep_gap) 模拟人为访问浏览器
    data_list = []
    # 爬取首页第一部分数据
    weibo_list, script = wh.access_homepage(user['user_id'])
    user['domid'] = script['domid']
    user['ns'] = script['ns']
    data_list += weibo_list
    put_scrap_info(scrap_id, wh.user, user['user_id'], '抓取第1页第1部分的%s条微博...' % len(weibo_list))
    write_file('%s/dump_weibo_list_new_1_00.json' % json_files, json.dumps(weibo_list), debug_flag)

    # 初始化
    page, pagebar = 1, 0
    # 爬取首页第二部分数据
    time.sleep(int(random.random() * sleep_gap))
    weibo_list, script, page, pagebar = load_more_weibo_info(wh, user, page, pagebar, scrap_id)
    data_list += weibo_list

    # 持续爬取首页第三部分数据至最终页数据
    while len(weibo_list) > 0:
        # 爬取加载更多的数据
        time.sleep(int(random.random() * sleep_gap))
        weibo_list, script, page, pagebar = load_more_weibo_info(wh, user, page, pagebar, scrap_id)
        data_list += weibo_list

        # 爬取翻页首部分数据
        if len(weibo_list) > 0 and pagebar == 2:
            time.sleep(int(random.random() * sleep_gap))
            weibo_list, script, page, pagebar = load_turn_page_weibo_info(wh, user, page, pagebar, scrap_id)
            data_list += weibo_list

    return data_list


def show(file):
    content = open(file).read()
    data_list = json.loads(content)
    print '==============================================================', len(data_list), '================================================================'
    for i, n in enumerate(data_list):
        for j in n:
            print j, ':', n[j]
        print
    print '=================================================================================================================================================='
    return len(data_list)


def get_user(user_list, user_number):
    user = user_list[user_number]
    user_id = user['user_id']
    print 'user_id', user_id
    return user


def scrap_main(username):
    # 传入用户名、名词参数，实例化weibo handler并登陆
    wh = log_in('13378423130', '133263.217')
    search_username = u'%s' % username
    # 获取搜索的用户结果
    user_list = wh.get_user_list(search_username)
    print generate_user_list_info(user_list)
    # 输入需要爬取信息的用户序号
    user = get_user(user_list, int(raw_input('choose:').strip()))
    # 正式爬取用户的所有微博数据
    data_list = scrap_user(wh, user)
    # 生成文件，写入数据库可以再调用写入数据库的接口
    write_file('scraped_weibo_files/%s.json' % search_username, json.dumps(data_list), debug_flag)
    # 入库测试
    batch_put_weibo_content(data_list)
    return data_list


def show_main():
    pages = 5
    pagebars = ('00', '0', '1')
    length = 0
    for page in range(1, pages+1):
        for pagebar in pagebars:
            if page == 5 and pagebar == '1':
                continue
            print '------', page, '-----', pagebar
            length += show('json_files/dump_weibo_list_new_%s_%s.json' % (page, pagebar))
    print 'total:', length

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # 抓取数据
    scrap_main('苗哥')

    # 写入数据库
    # content = open('scraped_weibo_files/huanglang_weibo.json').read()
    # data_list = json.loads(content)
    # for i in data_list:
    #     for j in i:
    #         if j not in ('pub_time', 'repost_from_pub_time', 'is_repost'):
    #             i[j] = json.dumps(i[j])
    # batch_put_weibo_content(data_list)

    # 展示数据
    show_main()
