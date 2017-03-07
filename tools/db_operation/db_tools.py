#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 数据库操作函数封装
################################################################
import json
import time
from sql_util import RainDB
from db_init import DB, CONTENT_INFO, USER_INFO, SCRAP_INFO


# ---------------------------------基本数据库操作函数封装--------------------------------------
def put_info(table, data):
    db = RainDB(DB)
    db.insert(table, data)
    db.db.commit()
    db.close()


def get_info(table, cond='1 = 1', desc='*'):
    db = RainDB(DB)
    data = db.select(table, cond, desc)
    db.close()
    return data


def update_info(table, cond, val):
    db = RainDB(DB)
    db.update(table, cond, val)
    db.db.commit()
    db.close()


def delete_info(table, cond):
    db = RainDB(DB)
    db.delete(table, cond)
    db.db.commit()
    db.close()
# -----------------------------------------------------------------------------------------------


def batch_put_info(table, data_list):
    db = RainDB(DB)
    for data in data_list:
        db.insert(table, data)
    db.db.commit()
    db.close()


# -----------------------------------------------------------------------------------------------


def get_weibo_content(user, cond='username'):
    # 获取某用户名或用户id的所有微博内容
    return get_info(CONTENT_INFO, "%s = '%s'" % (cond, user))


def batch_put_weibo_content(data_list):
    # 将所有的微博一条一条批量入库
    batch_put_info(CONTENT_INFO, data_list)


def save_user_log_info(user, prelog):
    db = RainDB(DB)
    res = db.select(USER_INFO, "user_account='%s'" % user)
    if len(res) == 0:
        db.insert(USER_INFO, {'user_account': user, 'prelog': json.dumps(prelog)})
    else:
        db.update(USER_INFO, "user_account='%s'" % user, {'prelog': "'" + json.dumps(prelog) + "'"})
    db.close()


def get_user_log_info(user):
    db = RainDB(DB)
    res = db.select(USER_INFO, "user_account='%s'" % user)
    db.close()
    return json.loads(res[0]['prelog']) if len(res) > 0 else {}


def put_scrap_info(scrap_id, log_user, scrap_user_id, return_content, stat_content=0):
    data = {
        'scrap_id': str(scrap_id),
        'log_user': log_user,
        'scrap_user_id': str(scrap_user_id),
        'return_content': return_content,
        'stat_content': str(stat_content),
        'run_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    put_info(SCRAP_INFO, data)


def get_scraped_weibo_info(username, keyword=''):
    result = get_info(CONTENT_INFO, " (content like '%%%(keyword)s%%' or repost_from_content like '%%%(keyword)s%%')"
                                    " and (username like '%%%(username)s%%' or user_id = '%(username)s') "
                                    "order by unixtime desc"
                      % {'keyword': keyword, 'username': username})
    return result
