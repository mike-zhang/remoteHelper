#! /usr/bin/python
#-*- coding:utf-8 -*-

import urllib
from hashlib import md5
import os,sys,time,random,string
import argparse,subprocess
import zlib,base64,uuid,ctypes,traceback

MAXEXPIRETIME = 24 * 3600  # seconds
_PDATA = '''
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
'''

class ConfigData():        
    def __init__(self,_fileName):
        self.fileName = _fileName
        self.docTree = None            
        self.getConfigFromFile()
 
    def getSectiontText(self,path):
        retText = ""
        if self.docTree :
            objTmp = self.docTree.find(path)
            if objTmp != None : 
                retText = objTmp.text                 
        return retText
        
    def getSectiontInt(self,path):    
        strTmp = self.getSectiontText(path).strip()
        return (int(strTmp) if strTmp.isdigit() else 0)    
    
    def getConfigFromFile(self):        
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET    
        if not os.path.exists(self.fileName) : 
            print "file ", self.fileName, " not exists"
            return None        
        try:
            self.docTree = ET.ElementTree(file=self.fileName)            
        except Exception,e:
            print "%s is NOT well-formed : %s "%(self.fileName,e)
            return None
        
        self.serial = self.getSectiontText("serial").strip()
        self.publicServer = self.getSectiontText("publicServer").strip()
        self.publicServerSSHUser = self.getSectiontText("publicServerSSHUser").strip()
        self.publicServerSSHPort = self.getSectiontInt("publicServerSSHPort")
        self.remoteUrl = self.getSectiontText("remoteUrl")
        self.local_ssh_port = self.getSectiontInt("local_ssh_port")
        self.local_http_port = self.getSectiontInt("local_http_port")
        self.tunnel_pid_path = self.getSectiontText("tunnel_pid_path") or "ssh_tunnel.pid"
        self.expire = self.getSectiontInt("expire") or 3600
        self.date_loop_path = self.getSectiontText("date_loop_path").strip()
        return None

    
def genKeypairs(keypath):    
    os.system("rm -f {0} {0}.pub".format(keypath))
    strcmd = "ssh-keygen -t rsa -f {keyfile} -N '' -b 1024"
    strcmd = strcmd.format(keyfile = keypath)
    os.system(strcmd)

def getPubkeyStr(keypath):
    ret = ""
    with open(keypath, 'rb') as fin :
        ret = fin.read().strip()
    return ret

def start_ssh_tunnel(cnf,dpwd,portsArr,pkey):        
    ret = True
    serial = cnf.serial
    ruser = cnf.publicServerSSHUser
    rhost = cnf.publicServer
    rsshPort = cnf.publicServerSSHPort
    date_loop_path = cnf.date_loop_path
    
    proxyPattern = "-R {0}:127.0.0.1:{1}"
    proxyStr = ""
    ssh_ports = {
        'proxy': 0,
        'source': 0,
    }
    http_ports = dict(ssh_ports)
    
    for ptype,lport,rport in portsArr:
        proxyStr += " %s " % proxyPattern.format(rport,lport)
        if ptype == 'ssh' :
            ssh_ports['source'] = lport
            ssh_ports['proxy'] = rport
        elif ptype == 'http' :
            http_ports['source'] = lport
            http_ports['proxy'] = rport
    strcmd = "ssh {0} -Cg -i {1} {2} {3}@{4} -p {5} {6} "    
   
    options = " -o StrictHostKeyChecking=no "
    
    dateloop = ""
    dateloop += " -sshPort {0} -sshSourcePort {1}".format(ssh_ports['proxy'], ssh_ports['source'])
    dateloop += " -httpPort {0} -httpSourcePort {1}".format(http_ports['proxy'], http_ports['source'])
    dateloop += " -rpd {0}".format(dpwd)
    dateloop += " -ttl {0}".format(cnf.expire)
    dateloop = "{0} -serial {1} {2}".format(date_loop_path,serial,dateloop)
    
    strcmd = strcmd.format(
        options,pkey,proxyStr,ruser,rhost,rsshPort,dateloop
    )
    print strcmd
    try:
        #os.system(strcmd)    
        psub = subprocess.Popen(strcmd,shell=True)
        print "pid is : {0}".format(psub.pid)
        with open(cnf.tunnel_pid_path, "w") as fout:
            fout.write(str(psub.pid))
    except:
        ret = False
    return ret
        

def add_auth_key_to_remote(serial,dpwd,urlbase):    
    # gen rsa key pairs    
    keyid = 'key_customer'
        
    genKeypairs(keyid)
    pubkey = getPubkeyStr(keyid+'.pub')   

    infmap = {
        'serial': serial,
        'cs' : md5(serial).hexdigest(),
        'key' : pubkey,
        'keycs' : md5(pubkey).hexdigest(),
        'dpd' : dpwd,
        'dpdcs' : md5(dpwd).hexdigest(),
    }
    params = urllib.urlencode(infmap)    
    url = "{0}?{1}".format(urlbase,params)
    print url
    f = urllib.urlopen(url)
    retPort = f.read().strip().split(',')
    flag,ssh_port, http_port = -1, 0, 0
    
    if len(retPort) == 3:
        print retPort
        flag = int(retPort[0])
        ssh_port = int(retPort[1])
        http_port = int(retPort[2])        
        if not flag == 0:
            pass        
    return flag,ssh_port,http_port,keyid

def do_ssh_proxy(cnf):
    ret = 0
    serial = cnf.serial
    urlbase = cnf.remoteUrl       
    ruser = cnf.publicServerSSHUser
    rhost = cnf.publicServer
    rport = cnf.publicServerSSHPort
    date_loop_path = cnf.date_loop_path
    dpwd = genDsaKeySeed(6)    
    flag,ssh_port,http_port,keyid = add_auth_key_to_remote(serial,dpwd,urlbase)

    if flag == 0:
        # ssh_port and http_port
        portsArr = [
            ('ssh', cnf.local_ssh_port, ssh_port),
            ('http', cnf.local_http_port, http_port), 
        ]
        if start_ssh_tunnel(cnf,dpwd,portsArr,keyid) :
            ret = 1
    elif flag == 1:
        ret = 2
    else :
        print "do_ssh_proxy : error occur"        
    return ret, dpwd

def addAuthKeys(pubkeyStr, expire=MAXEXPIRETIME):
    print "addAuthKeys"
    expireTime = int(time.time()) + expire
    checkDataCmd = "$(/bin/date '+%s') -lt {timestamp}"
    checkDataCmd = checkDataCmd.format(timestamp=expireTime)
    keyPattern = '''command="if [ {checkCmd} ]; then /bin/bash; else /bin/false; fi" '''
    keyPattern = keyPattern.format(checkCmd = checkDataCmd)
    keyPattern += '''{sshPubkey} # expire:{timestamp}'''.format(
        sshPubkey=pubkeyStr,timestamp=expireTime)
    print keyPattern
    home = os.path.expanduser('~')
    authfile = "{0}/.ssh/authorized_keys".format(home)
    with open(authfile,'a') as fout :
        fout.write(keyPattern + "\n")
    return None

def checkConnect(pulicHost):
    ret = False
    strcmd = "ps aux | grep ssh | grep key_customer |grep {0} | grep [d]ate_loop"
    strcmd = strcmd.format(pulicHost)
    print strcmd
    if os.popen(strcmd).read():
        ret = True
        print "already connect"
    else :
        print "not connect"
    return ret

def genDsaKeySeed(size=6):        
    values = string.ascii_letters + string.digits    
    seed = "".join(random.sample(values,size))
    print seed
    return seed

def _decodePData(_PDATA,outfile):
    data = "".join(_PDATA.split('\n'))    
    data = base64.b64decode(data)
    data = zlib.decompress(data)
    with open(outfile,"wb") as fout :
        fout.write(data)
    os.chmod(outfile,777)    

def doStart(cnf):    
    salt = "mysalt"    
    serial = cnf.serial
    remoteUrl = cnf.remoteUrl    
    print serial,remoteUrl        
    coninf = ""
    retStr = "serial : {0} ".format(serial)    
    if checkConnect(cnf.publicServer):        
        coninf = "already connect"
        retStr += ":{0}".format(coninf)
    else :
        ret,dpwd = do_ssh_proxy(cnf)
        if ret == 1:
            tpath = "/tmp/.{0}".format(uuid.uuid4())
            _decodePData(_PDATA,tpath)
            strcmd = '{pro} -b 1024 -s {salt} -p {passwd} -t 1'
            strcmd = strcmd.format(pro=tpath,salt=salt,passwd=dpwd)
            print strcmd
            dsaPubKey = os.popen(strcmd).read().strip()
            addAuthKeys(dsaPubKey,cnf.expire)
            os.remove(tpath)
            retStr += "\npassword : " + dpwd
    return retStr

def doStop(cnf):
    tpid = 0
    with open(cnf.tunnel_pid_path, "r") as fin:
        tpid = int(fin.read())
    if tpid :
        strcmd = "kill -9 {0}".format(tpid)
        print strcmd
        os.system(strcmd)
    return str(tpid)

if __name__ == "__main__" :
    parser = argparse.ArgumentParser(description='ssh tunnel option')
    parser.add_argument('-f', dest='conffile', action='store',
                        required=True,help='configure file')
    parser.add_argument('-o', dest='option', action='store',
                        required=True,help='start or stop')

    args = parser.parse_args()
    print(args.conffile)
    if not args.conffile :
        sys.exit(1)
    cnf = ConfigData(args.conffile)
    opt = args.option
    if opt == "start":
        doStart(cnf)
    elif opt == "stop":
        doStop(cnf)
