#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import MySQLdb
import MySQLdb.cursors
import traceback, cStringIO
pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
per = os.path.dirname(pwd)
sys.path.append(per)
from sqlstore import *

MAX_LIMIT = 10
mode = 'sql'
tmpfile = '/tmp/wsql.tmp'

regx = re.compile(u"([\u2e80-\uffff])", re.UNICODE)

def strException():
    sio = cStringIO.StringIO()
    traceback.print_exc(file=sio)
    s = sio.getvalue()
    sio.close()
    return s

def process_py(cmd):
    eval(cmd)

def process_sql(store, cmd):
    try:
        print cmd
        store.farm.execute(cmd)
        desc = store.farm.description
        keys = [item[0] for item in desc]
        content = store.farm.fetchall()
        if not content:
            print 'null result'
            return
        if len(content) > MAX_LIMIT: content = content[:MAX_LIMIT]
        for row in content:
            for k, v in row.items():
                #v = regx.sub(r'\1\0', str(v).decode('utf-8'))
                row[k] = str(v).decode('utf-8')
        key_len = {}
        for k in keys:
            #vl = [len(str(row[k])) for row in content]
            vl = [len(row[k]) for row in content]
            vl.append(len(str(k)))
            key_len[k] = max(vl)
        format_str = '|'
        for k in keys:
            format_str += ' %%(%s)-%ss |'%(k,key_len[k])
        ##print header
        hr = '-'*(sum(key_len.values())+3*len(key_len)+1)
        print hr
        print format_str%dict(zip(keys,keys))
        print hr
        for row in content:
            format_str = '|'
            for k in keys:
                ##the number of chinese words
                num_cw = len(regx.findall(row[k]))
                format_str += ' %%(%s)-%ss |'%(k,key_len[k]-num_cw)
            outstr = format_str%row
            print outstr
        print hr
    except:
        e = strException()
        print e

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
        prompt = '%s>'%mode
        #cmd = raw_input(prompt).strip()
        cmd = raw_input(prompt)
        if not cmd: continue
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
            if mode == 'py':
                process_py(cmd)
            elif mode == 'sql':
                process_sql(store, cmd)

    store.close()

if __name__ == '__main__':
    cmd_loop()
