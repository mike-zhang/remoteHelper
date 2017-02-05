#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os,threading,stat
import time

def deleteExpireKeys(authfile):
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
            
            expire_time = int(expireStr.split(":")[1])   
            if expire_time > cur_time:
                continue
            # do remove key
            print keysArr.pop()
            num_rm += 1
    if num_rm :            
        with open(authfile, 'w') as fout:
            fout.write("\n".join(keysArr))
    return None

def keyManager():
    homedir = os.path.expanduser('~')    
    authfile = "{0}/.ssh/authorized_keys".format(homedir)
    while True:
        try :
            if os.path.isfile(authfile) :
                deleteExpireKeys(authfile)
        except :
            pass            
        time.sleep(10)

def run():
    t = threading.Thread(target=keyManager)
    t.daemon = True
    t.start()
    
if __name__ == "__main__":
    keyManager() 
