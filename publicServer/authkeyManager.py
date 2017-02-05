#! /usr/bin/env python
#-*- coding:utf-8 -*-

from flask import Flask
from flask import request
from flask import render_template
import flask  
import hashlib, time
from socket import socket,inet_ntoa,AF_INET, SOCK_STREAM,SOCK_DGRAM
import os, sys, argparse, MySQLdb, common
import threading, stat
from common import ConfigData
import logging
import fcntl,struct

app = Flask(__name__)
app.debug = True

lock = threading.RLock()

MAXEXPIRETIME = 24 * 3600  # seconds

tb_tunnel = "ssh_tunnel_params"
gPortsMap = {
#    'serial' : {'ssh_port':10022},
}

logging.basicConfig(
    level=logging.DEBUG, # DEBUG,INFO,WARNING,ERROR,CRITICAL
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S'
)
logger = logging.getLogger()

def get_ip_address(ifname):
    s = socket(AF_INET, SOCK_DGRAM)
    return inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915, # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def addCmdPrefix(pubkeyStr, expireTime):    
    checkDataCmd = "$(/bin/date '+%s') -lt {timestamp}"
    checkDataCmd = checkDataCmd.format(timestamp=expireTime)
    keyPattern = '''command="if [ {checkCmd} ]; then /bin/bash; else /bin/false; fi" '''
    keyPattern = keyPattern.format(checkCmd = checkDataCmd)    
    keyPattern += '''{sshPubkey} # expire:{timestamp}'''.format(
        sshPubkey=pubkeyStr,timestamp=expireTime)    
    return keyPattern

def addAuthKeys(pubkeyStr):
    expireTime = int(time.time()) + MAXEXPIRETIME
    keyStr = '''{sshPubkey} # expire:{timestamp}'''.format(
        sshPubkey=pubkeyStr,timestamp=expireTime) 
    #keyStr = addCmdPrefix(pubkeyStr,expireTime)
    home = os.path.expanduser('~')
    authfile = "{0}/.ssh/authorized_keys".format(home)
    lock.acquire()
    with open(authfile,'a') as fout :
        fout.write(keyStr + "\n")
    lock.release()
    return None  
    
def getIdlePort():
    ret = 0
    #with socket(AF_INET,SOCK_STREAM) as sock:
    sock = socket(AF_INET,SOCK_STREAM)
    if sock :
        sock.bind(('',0))            
        ret = sock.getsockname()[1] 
        sock.close()
    return ret

def getDbConnector():
    cnf = ConfigData()
    params = [cnf.mysql_host,cnf.mysql_user,cnf.mysql_password,cnf.mysql_dbname,cnf.mysql_port]
    dbcon = common.ObjDBConnect(*params)
    return dbcon    

def checkSerialProxy(serial):
    query = "select count(*) from {0} where customer_serial = '{1}';"    
    query = query.format(tb_tunnel,serial)    
    dbcon = getDbConnector()    
    count = common.exeSqlAndGetNum(dbcon, query)
    return count == 0

@app.route('/', methods=['GET'])
def index():
    content = "<h4>authkeyManager<h4><ul>{0}</ul>"    
    content = "<html><body>%s<body><html>" % content
    #itemPatern = '<li><a href="/{0}" target="view_window">{1}</a></li>'
    itemPatern = '<li><a href="/{0}" target="_blank">{1}</a></li>'
    body = itemPatern.format("dosupport", "DoSupport")
    return content.format(body)     

def removeTunnelParamsPub(dbcon,params):
    serial,sshPort,httpPort = params    
    queryPattern = "delete from ssh_tunnel_params where customer_serial='{0}' and public_port = {1};"    
    sqlArr = []
    sqlArr.append(queryPattern.format(serial,sshPort))
    sqlArr.append(queryPattern.format(serial,httpPort))
    print sqlArr
    for query in sqlArr:
        dbcon.execute(query)
    dbcon.commit()

def _broker_not_proxy(serial,key):
    # not proxy yet , add keys
    addAuthKeys(key)
    ssh_port = getIdlePort()
    http_port = getIdlePort()
    idlePorts = {
        'ssh_port':ssh_port,
        'http_port':http_port,
    }
    if not serial in gPortsMap :
        gPortsMap[serial] = {}
    gPortsMap[serial].update(idlePorts)
    print gPortsMap
    ret = "0,%d,%d"%(ssh_port,http_port)
    return ret

def _broker(serial,cs,key,keycs):
    ret = ""
    md5 = hashlib.md5
    condition1 = serial and (cs == md5(serial).hexdigest())
    condition2 = key and (keycs == md5(key).hexdigest())
    if condition1 and condition2:
        if checkSerialProxy(serial) :
            ret = _broker_not_proxy(serial,key)                  
        else :
            qresult = getProxyPortsBySerial(serial)
            if qresult :
                ssh_port, http_port = 0, 0
                print qresult
                for _,local_port, source_port, tunnel_type in qresult :
                    if tunnel_type == 1 :  # ssh
                        ssh_port = local_port                    
                    elif tunnel_type == 2 :  # http
                        http_port = local_port
                strcmd = "ps aux | grep [d]ate_loop | grep {serial} | grep {ssh_port} |grep {http_port}"
                strcmd = strcmd.format(
                    serial=serial,
                    ssh_port=ssh_port,
                    http_port=http_port
                )
                print strcmd
                cmdResult =  os.popen(strcmd).read().strip()
                print cmdResult
                if cmdResult :
                    ret = "1,%d,%d"%(ssh_port,http_port)
                else:                    
                    params = [serial,ssh_port,http_port]
                    dbconn = getDbConnector()
                    removeTunnelParamsPub(dbconn,params)
                    dbconn.close()
                    ret = _broker_not_proxy(serial,key)                
    print "ret : ", ret
    return ret
    
@app.route('/tunnel-broker',methods=['GET','POST'])
def broker():
    ret = ""
    serial, cs, key, keycs = "","", "",""
    if request.method == 'POST':        
        logger.debug("POST data : {0}".format(str(request.form)))
    else :        
        tmap = request.args        
        logger.debug("GET data : {0}".format(tmap))
        serial = tmap.get('serial','')
        cs = tmap.get('cs','')
        key = tmap.get('key','')
        keycs = tmap.get('keycs','')
        
        trace = "serial : {0}\n".format(serial)
        trace += "cs : {0}\n".format(cs)
        trace += "key : {0}\n".format(key)
        trace += "keycs : {0}\n".format(keycs)
        logger.debug(trace)
        
    if all([serial, cs, key, keycs]):
        ret = _broker(serial,cs,key,keycs)
    return ret

def getProxyPortsBySerial(serial):
    cnf = ConfigData()    
    params = [cnf.mysql_host,cnf.mysql_user,cnf.mysql_password,cnf.mysql_dbname,cnf.mysql_port]
    print params
    dbcon = common.ObjDBConnect(*params)
    query = "select random_password,public_port,source_port,tunnel_type from {0} ".format(tb_tunnel)
    query += " where customer_serial = '{0}';".format(serial)
    print serial
    print '*' * 30
    print query
    return dbcon.execWithRet(query)    

def getQueryResult(serial):
    ret = {}
    query_result = getProxyPortsBySerial(serial)
    if query_result :        
        for random_password,public_port, source_port, tunnel_type in query_result :
            if tunnel_type == 1 :  # ssh               
                ret.update({
                    'ssh_port' : public_port,
                    'random_password' : random_password,                    
                })
            elif tunnel_type == 2 :  # http
                ret.update({
                    'http_port' : public_port,
                })
    return ret

@app.route('/query',methods=['GET','POST'])
def query():
    ret = ""
    if request.method == "POST" :
        print request.form
    else :        
        tmap = request.args
        print tmap
        serial = tmap.get('serial')
        ret = getQueryResult(serial)
        ret = flask.jsonify(**ret)
    return ret

@app.route('/dosupport', methods=['GET','POST'])
def dosupport():
    ret = ""
    if request.method == "POST" :
        print request.form
        tmap = request.form
        serial = tmap.get('serial')        
        qret = getQueryResult(serial)
        if qret :        
            webPort = qret.get("http_port", "0")
            sshPort = qret.get("ssh_port", "0")
            print webPort, sshPort
            print qret
            ret = render_template(
                'dosupport.html',
                serial=serial,
                rpd=qret.get("random_password", ""),                
                httpIP=get_ip_address('eth0'),
                httpPort=webPort,
                sshPort=sshPort, 
            )
        else :
            ret = "serial({0}) not connected!".format(serial)        
    else :        
        tmap = request.args
        print tmap
        serial = tmap.get('serial')
        qret = getQueryResult(serial)              
        webPort = qret.get("http_port", "")
        print webPort
        ret = render_template(
            'dosupport.html',
            serial=serial,
            rpd=qret.get("random_password", ""),
            sshPort=qret.get("ssh_port", "0"),
            httpIP=get_ip_address('eth0'),
            httpPort=webPort)
    return ret    

def create_auth_files(homedir,authfile):
    sshdir = "{0}/.ssh".format(homedir)
    if not os.path.isdir(sshdir):
        os.mkdir(sshdir)    
        os.chmod(sshdir,stat.S_IRWXU)    
    open(authfile,'a').close()
    os.chmod(authfile,stat.S_IWRITE | stat.S_IREAD)
    return None    
    
def keyManager():
    homedir = os.path.expanduser('~')    
    authfile = "{0}/.ssh/authorized_keys".format(homedir)
    if not os.path.isfile(authfile) :
        create_auth_files(homedir,authfile)    
    while True:
        lock.acquire()
        keysArr = []
        validKeys = ""
        cur_time = time.time()
        num_rm = 0
        with open(authfile,'r') as fin :
            for line in fin :
                line = line.strip()
                if not line : continue
                keysArr.append(line)
                arrtmp = line.split("#")
                if len(arrtmp) != 2:
                    continue
                expireStr = arrtmp[1]
                if expireStr.find("expire") == -1:
                    continue
                # expire:1456212447            
                expire_time = int(expireStr.split(":")[1])
                if expire_time > cur_time:
                    continue
                # do remove key
                print keysArr.pop()
                num_rm += 1
        if num_rm :            
            with open(authfile, 'w') as fout:
                fout.write("\n".join(keysArr))
        lock.release()
        time.sleep(5)
    
def main():   
    parser = argparse.ArgumentParser(description='ssh key manage server')
    parser.add_argument('-f', dest='conffile', action='store',
                        required=True,help='configure file')    
    args = parser.parse_args()
    print(args.conffile)
    if not args.conffile :
        sys.exit(1)    
    conffile = args.conffile
    
    cnf = ConfigData()
    cnf.load(conffile)
    t = threading.Thread(target=keyManager)
    t.daemon = True
    t.start()    
    print "listen on port {0}".format(cnf.listenPort)
    app.run(host="0.0.0.0",port=cnf.listenPort)
 
if __name__ == '__main__':
    main()
