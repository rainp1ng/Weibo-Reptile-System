#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################
# 数据库初始化
################################################################
from sql_util import RainDB
DB = 'weibo_reptile'
USER_INFO = 'user_info'
CONTENT_INFO = 'content_info'
SCRAP_INFO = 'scrap_info'


# 用户登录信息表
user_cols = [
    'user_account varchar(255)',
    'prelog text',
]


# 用户微博内容表
content_cols = [
    'user_id varchar(255)  ',
    'link varchar(255) ',
    'username varchar(255) ',
    'pub_time datetime ',
    'unixtime varchar(255) ',
    'pub_dev varchar(255) ',
    'content text ',
    'content_pics text ',
    'content_link text ',
    'is_repost int ',
    'repost_from_link varchar(255) ',
    'repost_from_username varchar(255) ',
    'repost_from_pub_time datetime ',
    'repost_from_unixtime varchar(255) ',
    'repost_from varchar(255) ',
    'repost_from_content text ',
    'repost_from_content_pics text ',
    'repost_from_content_link text ',
    'pictures text',
    'videos text'
]


scrap_cols = [
    'id int primary key not null auto_increment ',
    'scrap_id int not null default 0',
    'log_user varchar(255) not null',
    'scrap_user_id varchar(255) not null',
    'return_content text',
    'stat_content int',
    'run_time datetime'
]


def main():
    # 初始化数据库weibo_reptile
    db = RainDB(DB)
    # 创建存储登录时用户信息的表
    db.drop_table(USER_INFO)
    db.create_table(USER_INFO, user_cols)
    # 创建存储微博内容的表
    db.drop_table(CONTENT_INFO)
    db.create_table(CONTENT_INFO, content_cols)
    # 创建存储爬取状况信息的表
    db.drop_table(SCRAP_INFO)
    db.create_table(SCRAP_INFO, scrap_cols)


if __name__ == '__main__':
    main()
