#-*- coding:utf-8 -*-

import MySQLdb,threading
import os

class ObjDBConnect():
    conn = None
    cursor = None
    
    def __init__(self,host,user,passwd,dbname,port):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.port = port     
        
    def connect(self,tryTimes=1):
        i = 0
        while i < tryTimes :                      
            try :
                self.conn = MySQLdb.connect(self.host,self.user,self.passwd,self.dbname,self.port,charset="utf8")
                break
            except : 
                i += 1
                #self.log.error("connect db error")
        return self.conn        
        
    def execute(self,sql):
        '''exec sql insert or delete'''
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except (AttributeError,MySQLdb.OperationalError, MySQLdb.DatabaseError):
            self.connect()
            if self.conn :
                cursor = self.conn.cursor()
                cursor.execute(sql)
        return cursor    
    
    def commit(self):
        if self.conn : self.conn.commit()
        
    def rollback(self):
        if self.conn : self.conn.rollback()
        
    def execWithRet(self,sql):
        '''exec sql query '''
        retList = []
        try :
            cursor = self.conn.cursor()            
            count = cursor.execute(sql)
            retList = cursor.fetchmany(count)          
        except (AttributeError, MySQLdb.OperationalError, MySQLdb.DatabaseError):            
            self.connect()
            if self.conn :
                cursor = self.conn.cursor()
                count = cursor.execute(sql)
                retList = cursor.fetchmany(count) 
        except :
            retList = []   
        return retList

    def getTableFields(self,tbName):
        tbFileds = []
        query = "desc {}".format(tbName)
        for item in self.execWithRet(query):
            tbFileds.append(item[0])
        return tbFileds
  
    def close(self):
        if(self.cursor):
            self.cursor.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()
            
def exeSqlAndGetNum(dbConn, query):    
    retVavlue = 0  
    tmpList = dbConn.execWithRet(query)
    if len(tmpList) == 1 :             
        if str(tmpList[0][0]).isdigit(): retVavlue = int(tmpList[0][0])            
    return retVavlue

class Singleton(type):
    """
    A singleton metaclass. 
    
    usage :
        class A():
            __metaclass__ = Singleton 
            def __init__(self):
                pass
    """
    def __init__(cls, name, bases, dictionary):
        super(Singleton, cls).__init__(name, bases, dictionary)
        cls._instance = None
        cls._rlock = threading.RLock()
    def __call__(cls, *args, **kws):
        with cls._rlock:
            if cls._instance is None:
                cls._instance = super(Singleton, cls).__call__(*args, **kws)
        return cls._instance
    
class ConfigData():
    __metaclass__ = Singleton 
    def __init__(self):        
        self.docTree = None
        self.acl = []
        
    def load(self,fileName):        
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

    def getAclIps(self):        
        if not self.docTree : 
            return None            
        objTmp = self.docTree.findall("acl/ip")            
        if objTmp :
            self.acl += [item.text for item in objTmp]            
            #print [item.text for item in objTmp]            
        return None
    
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
        self.publicIP = self.getSectiontInt("publicIP")
        self.listenPort = self.getSectiontInt("listenPort")
        self.max_connect_time = self.getSectiontInt("max_connect_time")
        
        self.mysql_host = self.getSectiontText("mysql/host")
        self.mysql_port = self.getSectiontInt("mysql/port")
        self.mysql_user = self.getSectiontText("mysql/user")
        self.mysql_password = self.getSectiontText("mysql/password") or ""
        self.mysql_dbname = self.getSectiontText("mysql/dbname")
        
        self.enable_acl = self.getSectiontInt("enable_acl")
        if self.enable_acl :
            self.getAclIps()        
        
        return None

    
