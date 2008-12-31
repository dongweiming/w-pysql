#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import MySQLdb
import MySQLdb.cursors
pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
per = os.path.dirname(pwd)
sys.path.append(per)
from sqlstore import *

MAX_LIMIT = 10
mode = 'sql'
tmpfile = '/tmp/wsql.tmp'

def get_store(conf):
    return SqlStore(host=conf['host'],user=conf['user'],passwd=conf['passwd'],\
            db=conf['db'],port=conf['port'],cursorclass=MySQLdb.cursors.DictCursor)

def cmd_loop():
    print '''Welcome to wsql,
press "q" to exit,
press "use **" to switch database,
press sql command to query mysql.\n'''
    global MAX_LIMIT, mode
    store = get_store(luz2)
    while 1:
        print '%s>'%mode,
        cmd = raw_input().strip()
        if cmd == 'q':
            print 'exit'
            break
        elif cmd[:4].lower() == 'use ':
            db = cmd.split()[-1]
            print db
            store.close()
            store = get_store(eval(db))
        elif cmd == 'mode':
            if mode == 'sql': mode = 'py'
            else: mode='sql'
        elif cmd[:4].lower() == 'limit ':
            MAX_LIMIT = cmd.split()[-1]
        else:
            print cmd
            store.farm.execute(cmd)
            desc = store.farm.description
            keys = [item[0] for item in desc]
            content = store.farm.fetchall()
            if not content:
                print 'null result'
            if len(content) > MAX_LIMIT: content = content[:MAX_LIMIT]
            key_len = {}
            for k in keys:
                vl = [len(str(row[k])) for row in content]
                vl.append(len(str(k)))
                key_len[k] = max(vl)
            format_str = ''
            for k in keys:
                format_str += '%%(%s)-%ss|'%(k,key_len[k]+3)
            print format_str%dict(zip(keys,keys))
            for row in content:
                print format_str%row

    store.close()

if __name__ == '__main__':
    cmd_loop()
