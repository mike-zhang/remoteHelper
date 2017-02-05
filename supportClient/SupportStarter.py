#! /usr/bin/env python
#-*-coding:utf-8-*-

import os,sys
import threading,subprocess

class ConfigData():    
    def __init__(self,fileName):        
        self.docTree = None
        self.getConfigFromFile(fileName)        
 
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
    
    def getConfigFromFile(self,fileName):        
        try:
            import xml.etree.cElementTree as ET
        except ImportError:
            import xml.etree.ElementTree as ET    
        if not os.path.exists(fileName) : 
            print "file ", fileName, " not exists"
            return None        
        try:
            self.docTree = ET.ElementTree(file=fileName)            
        except Exception,e:
            print "%s is NOT well-formed : %s "%(fileName,e)
            return None
        self.pubServer = self.getSectiontText("pubServer")
        self.remoteUser = self.getSectiontText("remoteUser")
        
        return None

def startSSHTunnel(workdir,ppkeyfile,ruser,rhost,rport):
    if os.path.isfile(ppkeyfile):        
        puttyPath = os.path.join(workdir,"putty.exe")
        strcmd = "{0} -ssh -i {1} {2}@{3} -P {4} "        
        strcmd = strcmd.format(puttyPath,ppkeyfile,ruser,rhost,rport)        
        print strcmd
        child = subprocess.Popen(strcmd,shell=True)
    return 0  
    
def startScpTunnel(workdir,ppkeyfile,ruser,rhost,rport):
    if os.path.isfile(ppkeyfile):
        # winscp.exe scp://root@192.168.131.123:47098/ /privatekey=c://supportClient/key1.ppk
        scpPath = os.path.join(workdir, "WinSCP.exe")
        strcmd = "{0} scp://{1}@{2}:{3}/ /privatekey={4}"
        strcmd = strcmd.format(scpPath, ruser, rhost, rport, ppkeyfile)      
        print strcmd
        child = subprocess.Popen(strcmd,shell=True)
    return 0      

def doProxy(appname,workdir,randPwd,ruser,rhost,rport):
    strcmd = "{0}\\gendsa.exe -b 1024 -s mysalt -p {1} -t 2"    
    strcmd = strcmd.format(workdir,randPwd)
    print strcmd
    keybuf = os.popen(strcmd).read()
    sshkeyfile = os.path.join(workdir,"key1.pem")
    ppkeyfile = os.path.join(workdir,"key1.ppk")
    with open(sshkeyfile, 'w') as fout :
        fout.write(keybuf)
    if os.path.isfile(sshkeyfile) :
        winscpPath = os.path.join(workdir, "winscp.com")
        strcmd = "{0} /keygen {1} /output={2}"
        strcmd = strcmd.format(winscpPath,sshkeyfile,ppkeyfile)
        child = subprocess.Popen(strcmd,shell=True)
        child.wait()        
        os.remove(sshkeyfile)
    if appname == "putty":
        startSSHTunnel(workdir,ppkeyfile,ruser,rhost,rport)
    elif appname == "winscp":
        startScpTunnel(workdir,ppkeyfile,ruser,rhost,rport)
    return None

def start_app(workdir,serial,randPwd,ssh_port,appname):        
    cnf = ConfigData(os.path.join(workdir,"default.xml"))    
    ruser = cnf.remoteUser
    rhost = cnf.pubServer
    t = threading.Thread(
        target=doProxy,
        args=(appname,workdir,randPwd,ruser,rhost,ssh_port))
    #t.daemon = True
    t.start()
    #t.join()
    return None

if __name__ == "__main__" :
    argv = sys.argv
    workdir = os.path.dirname(os.path.realpath(argv[0]))
    print argv    
    if len(argv) < 2 :
        sys.exit(1)
            
    pstr = argv[1]
    arr = pstr.split("://")    
    tmpstr = str(arr[1][0:-1])    
    dtmp = {}
    for item in tmpstr.split(','):
        print 'item : {0}'.format(item)
        tarr = item.split("=")
        print tarr
        if len(tarr) == 2 :
            k, v = tarr
            dtmp[k] = v
    print dtmp    
    serial = dtmp.get('serial')
    rpd = dtmp.get('rpd')
    ssh_port = dtmp.get('ssh_port')
    appname = dtmp.get('appname')    
    print "serial : {0}".format(serial)
    start_app(workdir,serial,rpd,ssh_port,appname)
    
