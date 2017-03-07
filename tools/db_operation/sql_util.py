#!/usr/bin/python
# -*- coding:utf-8 -*-
import MySQLdb


HOST = "localhost"
USER = "root"
PASSWD = 'wwwscuteducn'  # raw_input('mysql password:').strip()
PORT = 3306
CHARSET = "utf8"


def connect():
    return MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, port=PORT, charset=CHARSET)


def parse_json(desc, rows):
    if len(rows) == 1:
        results = {}
        row = rows[0]
        i = 0
        for u_desc in desc:
            results[u_desc[0]] = str(row[i])
            i += 1
        results = [results]
    else:
        results = []
        for row in rows:
            i = 0
            result = {}
            for u_desc in desc:
                result[u_desc[0]] = str(row[i])
                i += 1
            results.append(result)
    return results


class RainDB(object):
    def __init__(self, db_name="", encode="utf8mb4"):
        self.encoding = encode
        self.db = connect()
        self.cursor = self.db.cursor()
        if db_name != "":
            self.create_database(db_name)
            self.db.select_db(db_name)
        self.cursor.execute("SET NAMES utf8mb4")

    def close(self):
        self.cursor.close()
        self.db.close()

    def create_database(self, db_name):
        self.cursor.execute("create database if not exists %s character set %s" % (db_name, self.encoding))
        self.db.commit()

    def create_table(self, table_name, rows):
        sql_query = "show tables like '%s'" % table_name
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if len(res) != 0:
            return
        sql_str = "create table if not exists %s(" % table_name
        for i, row in enumerate(rows):
            sql_str += row
            if i != len(rows)-1:
                sql_str += ","
        sql_str += ") charset %s" % self.encoding
        # print sql_str
        self.cursor.execute(sql_str)
        self.db.commit()
        print "create table %s" % table_name

    def drop_table(self, table_name):
        sql_query = "show tables like '%s'" % table_name
        self.cursor.execute(sql_query)
        res = self.cursor.fetchall()
        if len(res) == 0:
            return
        d = raw_input("Press y to drop table %s ." % table_name)
        if d == "y":
            self.cursor.execute("drop table %s" % table_name)
            self.db.commit()
        else:
            print "table %s is not dropped ." % table_name

    def insert(self, table, val):
        n_desc = "("
        n_val = "('"
        for i, desc in enumerate(val):
            n_desc += desc + ","
            n_val += self.db.escape_string(val[desc])+"','"
            if i == len(val)-1:
                n_desc = n_desc[:len(n_desc)-1]+")"
                n_val = n_val[:len(n_val)-2]+")"
        sql_str = "insert into %s %s value %s " % (table, n_desc, n_val)
        # print sql_str
        self.cursor.execute(sql_str)
        # self.db.commit()

    def select(self, table, cond="1=1", desc="*", model=""):
        sql_str = "select %s from %s where %s" % (desc, table, cond)
        print sql_str
        self.cursor.execute(sql_str)
        r_desc = self.cursor.description
        rows = self.cursor.fetchall()
        results = parse_json(r_desc, rows)
        return results

    def delete(self, table, cond="1=1"):
        sql_str = "delete from %s where %s" % (table, cond)
        self.cursor.execute(sql_str)
        # self.db.commit()

    def update(self, table, cond, val):
        n_val = ""
        for i, desc in enumerate(val):
            n_val += desc + " = "+val[desc]
            if i != len(val)-1:
                n_val += ","
        sql_str = "update %s set %s where %s" % (table, n_val, cond)
        print sql_str
        self.cursor.execute(sql_str)
        # self.db.commit()
