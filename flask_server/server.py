#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 服务器程序
################################################################
import json
import time
import traceback
from flask import Flask, abort, render_template, redirect, send_from_directory, request, make_response
from flask.ext.bootstrap import Bootstrap
from tools.http_tools import WeiboHandler
from tools.db_operation.db_tools import save_user_log_info, get_user_log_info, batch_put_info, CONTENT_INFO, SCRAP_INFO, put_info, get_info, put_scrap_info, get_scraped_weibo_info
from tools.__init__ import debug_flag
from tools.scrap_tools import scrap_user
from multiprocessing import Process
global log_handler
global search_user_list
log_handler = {}
search_user_list = {}
process_list = []


server = Flask(__name__)
bootstrap = Bootstrap(server)


def read_wh(username):
    if log_handler.get(username) is None:
        log_handler[username] = WeiboHandler(username, '', 'flask_server/static/png/')
    return log_handler[username]


def read_cookie():
    username = request.cookies.get('username')
    if username is None:
        user_list = []
    else:
        user_list = [{'username': username}]
    return user_list


@server.route('/')
def index():
    user_list = read_cookie()
    return render_template('index.html', user_list=user_list)


@server.route('/signup')
def sign_up():
    return redirect('http://weibo.com/signup/signup.php')


@server.route('/login', methods=['POST'])
def log_in():
    username = request.form['id']
    wh = read_wh(username)
    wh.passwd = request.form['passwd']
    vercode = request.form['vercode']
    log_flag = request.form['logflag']
    if log_flag == '1':
        resp = make_response(json.dumps({'stat': '200', 'furl': request.form['ip']}))
        resp.set_cookie('username', username)
        return resp
    # log_handler.prelog_data = get_user_log_info(username)
    data2, replace_url = wh.do_log_req(vercode)
    if int(data2['retcode'][0]) == 0:
        wh.final_log_req(replace_url)
        resp = make_response(json.dumps({'stat': '200', 'furl': request.form['ip']}))
        resp.set_cookie('username', username)
        return resp
    print 'Log in failed ... retcode:', data2['retcode'][0], ', reason:', data2['reason'][0].decode('gbk')
    no = wh.get_vercode()
    return json.dumps({'stat': '502', 'reason': data2['reason'][0].decode('gbk'), 'vercode_no': no})


@server.route('/check_log', methods=['POST'])
def check_log():
    username = request.form['id']
    wh = read_wh(username)
    wh.check_log_status(wh.open_weibo_page())
    if wh.log_flag:
        return json.dumps({'stat': '200'})
    prelog = wh.prelog()
    # save_user_log_info(username, prelog)
    try:
        if prelog['showpin'] == 1:
            no = wh.get_vercode()
            return json.dumps({'stat': '502', 'vercode_no': no})
        return json.dumps({'stat': '501'})
    except Exception, e:
        return json.dumps({'stat': '501'})


@server.route('/logout')
def log_out():
    resp = make_response(redirect('/'))
    resp.set_cookie('username', '', expires=0)
    return resp


@server.route('/static/<path:path>')
def send_static_file(path):
    return send_from_directory('static', path)


@server.route('/search_user/<word>')
def search_user(word):
    username = request.cookies.get('username')
    wh = read_wh(username)
    if username is None:
        return {'stat': '404'}
    search_user_list[username] = wh.get_user_list(word)
    if debug_flag:
        print search_user_list
    return json.dumps({'stat': '200', 'result': search_user_list[username]})


@server.route('/scrap/<user_no>')
def to_scrap(user_no):
    username = request.cookies.get('username')
    if username is None:
        return render_template('index.html')
    user = search_user_list[username][int(user_no)]
    last_record = get_info(SCRAP_INFO, cond=' 1=1 order by id desc limit 1')
    scrap_id = 0 if len(last_record) == 0 else (int(last_record[0]['id']) + 1)
    put_scrap_info(scrap_id, username, user['user_id'], '开始爬取%s的所有微博内容...' % user['title'])
    sp = Process(target=scrap_process, name='%s_%s_%s' % (username, user['user_id'], scrap_id), args=(username, user, scrap_id))
    sp.start()
    process_list.append(sp)
    return redirect('/scrap_listen?d=%s' % scrap_id)


@server.route('/scrap_listen', methods=['GET'])
def scrap_listen():
    scrap_id = request.args.get('d')
    if debug_flag:
        print scrap_id
    user_list = read_cookie()
    return render_template('scrap_listen.html', scrap_id=scrap_id, user_list=user_list)


@server.route('/read_scrap/<scrap_id>/<last_message_id>')
def read_scrap(scrap_id, last_message_id):
    data = get_info(SCRAP_INFO, cond=' scrap_id=%s and id > %s ' % (scrap_id, last_message_id))
    return json.dumps(data)


def scrap_process(username, user, scrap_id):
    try:
        wh = read_wh(username)
        data_list = scrap_user(wh, user, scrap_id, 0)
        batch_put_info(CONTENT_INFO, data_list)
        put_scrap_info(scrap_id, username, user['user_id'], '爬取完毕!共爬取%s%s条微博.保存至数据库....' % (user['title'], len(data_list)), 1)
    except Exception, e:
        traceback.print_exc()
        put_scrap_info(scrap_id, username, user['user_id'], '出现异常,数据未保存,请重新爬取数据!', -1)


@server.route('/search')
def search_scrap_result():
    user_list = read_cookie()
    return render_template('/search.html', user_list=user_list)


@server.route('/search_scraped_weibo/<username>', methods=['GET'])
def search_scraped_weibo(username):
    print 'here'
    keyword = request.args.get('keyword')
    print 'there'
    if keyword is None:
        weibo_list = get_scraped_weibo_info(username)
    else:
        weibo_list = get_scraped_weibo_info(username, keyword)
    return json.dumps({'stat': '200', 'result': weibo_list})
