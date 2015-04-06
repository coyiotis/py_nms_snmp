import re, collections
import sys
from subprocess import *
import os,sys,subprocess,threading
import MySQLdb


def check_db(db):
    cursor = db.cursor()
    sql = """SELECT * 
             FROM information_schema.tables
             WHERE table_schema = 'monitoringdb' 
             AND table_name = 'nodes'
             LIMIT 1;"""
    cursor.execute(sql)        
    data = cursor.fetchone()
    
    if data != None:
        pass
    else:
        print "empty! Creating table \"nodes\" "
    
        # Create table as per requirement
        sql = """CREATE TABLE nodes (
                NodeID  CHAR(20) NOT NULL,
                NodeIP  CHAR(15) NOT NULL,
                NodePORT CHAR(15) NOT NULL,
                FreeRAM  CHAR(15) NOT NULL,
                TotalRAM CHAR(15) NOT NULL,
                FreeD CHAR(15) NOT NULL,  
                TotalD CHAR(15) NOT NULL,
                CPU CHAR(15) NOT NULL )"""
        
        cursor.execute(sql)
        
        
def call_and_peek_output(cmd, shell=False):
    import pty, subprocess
    master, slave = pty.openpty()
    p = subprocess.Popen(cmd, shell=shell, stdin=None, stdout=slave, close_fds=True)
    os.close(slave)
    line = ""
    while True:
        try:
            ch = os.read(master, 1)
        except OSError:
            break
        line += ch
        if ch == '\n':
            yield line
            line = ""
    if line:
        yield line

    ret = p.wait()
    if ret:
        raise subprocess.CalledProcessError(ret, cmd)


def fetch_stats(ip,port):
    cmd = 'snmpwalk -c public -v 2c ' + ip + ':' + port + ' iso.3.6.1.2.1.1'
    stats={}
    for line in call_and_peek_output([cmd], shell=True):
        if 'iso.3.6.1.2.1.1.11.0' in line:
            stats['freeram']=line.split('STRING: \"',1)[1].split('\"',1)[0]
        elif 'iso.3.6.1.2.1.1.11.1' in line:
            stats['totalram']=line.split('STRING: \"',1)[1].split('\"',1)[0]
        elif 'iso.3.6.1.2.1.1.12.0' in line:
            stats['freed']=line.split('STRING: \"',1)[1].split('\"',1)[0]
        elif 'iso.3.6.1.2.1.1.12.1' in line:
            stats['totald']=line.split('STRING: \"',1)[1].split('\"',1)[0]
        elif 'iso.3.6.1.2.1.1.13.0' in line:
            try:
                stats['cpu']=line.split('STRING: \"',1)[1].split('\"',1)[0]
            except:
                pass
        elif 'timeout' in line:
            print "Host " + ip + " not available, or bad port number!"
            
    return stats


def update_db(db):
    check_db(db)
    cursor = db.cursor()
    sql = 'select nodeip from nodes'
    try:
        cursor.execute(sql)
        iplist = cursor.fetchall()
        for item in iplist:
            sql = "select nodeport from nodes where nodeip='%s'" % item[0]
            cursor.execute(sql)
            port=cursor.fetchall()
            port = port[0][0]
            stats = {}
            try:
                stats = fetch_stats(item[0], port)
            except:
                print "Host " + item[0] + " not available!"
            if stats != {} :
                sql = "update nodes set freeram='%s', totalram='%s', freed='%s', totald='%s', cpu='%s' where nodeip='%s'" % \
                       (stats['freeram'], stats['totalram'], stats['freed'], stats['totald'], stats['cpu'], item[0] )
            cursor.execute(sql)
            outp = cursor.fetchall()
    except:
        db.rollback()
