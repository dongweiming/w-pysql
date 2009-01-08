#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import MySQLdb
import MySQLdb.cursors
import traceback, cStringIO
import time
pwd = os.path.dirname(os.path.realpath(sys.argv[0]))
per = os.path.dirname(pwd)
sys.path.append(per)
from sqlstore import *
from tools import q_query

regx = re.compile(u"([\u2e80-\uffff])", re.UNICODE)
reqt = re.compile('[\w\d\s](=)[\w\d\s]')

def strException():
    sio = cStringIO.StringIO()
    traceback.print_exc(file=sio)
    s = sio.getvalue()
    sio.close()
    return s

class Option():
    def __init__(self):
        self.limit = 100
        self.mode = 'sql'
        self.mlist = ('sql','py','kdb')
        self.khost = 'boromir'

    def set_mode(self, arg):
        if arg in self.mlist:
            self.mode = arg
        else:
            print 'mode argument must in', self.mlist

    def set_limit(self, arg):
        self.limit = arg

    def set_khost(self, arg):
        self.khost = arg

class Processor():
    def __init__(self, opt):
        self.tc = 0.0

    def process(self, cmd):
        pass

class SQLProcessor(Processor):
    def __init__(self, opt):
        self.tc = 0.0
        self.opt = opt

    def process(self, store, cmd):
        print cmd
        ot = time.time()
        store.farm.execute(cmd)
        self.tc = time.time() - ot
        desc = store.farm.description
        keys = [item[0] for item in desc]
        content = store.farm.fetchall()
        if not content:
            print 'null result'
            return
        if len(content) > self.opt.limit: content = content[:self.opt.limit]
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

class KDBProcessor(Processor):
    def __init__(self, opt):
        self.tc = 0.0
        self.opt = opt

    def process(self, cmd):
        cmd = '%s#%s'%(self.opt.limit, cmd)
        ot = time.time()
        data = q_query(cmd, host=self.opt.khost)
        self.tc = time.time() - ot
        for row in data:
            print ' '.join(row)

class Store():
    def __init__(self):
        self.store = self.get_store(luz2)
        self.farm = self.store.farm

    def get_store(self, conf):
        return SqlStore(host=conf['host'],user=conf['user'],passwd=conf['passwd'],\
                db=conf['db'],port=conf['port'],cursorclass=MySQLdb.cursors.DictCursor)

    def switch(self, conf):
        self.store = self.get_store(conf)
        self.farm = self.store.farm

    def close(self):
        self.store.close()

class CMD_loop():
    def __init__(self):
        self.opt = Option()
        self.store = Store()
        self.sqlp = SQLProcessor(self.opt)
        self.kdbp = KDBProcessor(self.opt)
        self.cmd = ''
        self.show_help()

    def show_help(self):
        print '''Welcome to wsql, \npress "q" to exit, \npress "use **" to switch database, \npress sql command to query mysql.\n'''

    def run(self):
        while 1:
            self.prompt = '%s>'%self.opt.mode
            self.cmd = raw_input(self.prompt).strip()
            if not self.cmd: continue
            if self.cmd == 'q':
                print 'exit'
                break
            elif self.cmd[:4].lower() == 'use ':
                db = self.cmd.split()[-1]
                self.store.close()
                if db[-1].isdigit():
                    dbconf = eval(db)
                else:
                    dbconf = eval(db+'conf')
                print 'DB config:', dbconf
                self.store.switch(dbconf)
            elif self.cmd[:6].lower() == 'limit ':
                self.opt.set_limit(int(self.cmd.split()[-1]))
            elif self.cmd[:5].lower() == 'host ':
                self.opt.set_khost(self.cmd.split()[-1])
            elif self.cmd[:5].lower() == 'mode ':
                self.opt.set_mode(self.cmd.split()[-1])
            else:
                try:
                    if self.opt.mode == 'py':
                        reobj = reqt.search(self.cmd)
                        if not reobj:
                            ##expression
                            print eval(self.cmd)
                        else:
                            ##statement
                            exec self.cmd
                    elif self.opt.mode == 'sql':
                        try:
                            ##passed from py mode
                            self.cmd = eval(self.cmd)
                        except SyntaxError:
                            pass
                        self.sqlp.process(self.store, self.cmd)
                        print 'time cost: %8.4f sec\n'%self.sqlp.tc
                    elif self.opt.mode == 'kdb':
                        self.kdbp.process(cmd)
                        print 'time cost: %8.4f sec\n'%self.kdbp.tc
                except:
                    self.e = strException()
                    print self.e

        self.store.close()


if __name__ == '__main__':
    loop = CMD_loop()
    loop.run()
