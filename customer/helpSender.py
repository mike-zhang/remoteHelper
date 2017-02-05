#! /usr/bin/env python
#-*- coding:utf-8 -*-

from flask import Flask
from flask import render_template,request
from sshTunnelOpt import  ConfigData,doStart,doStop

app = Flask(__name__, static_folder="templates")
app.debug = False

dynamicPassword = ""
gconfig = None

def getParam(key):
    value = ""
    try :
        if request.method == 'POST':
            value = request.form[key]
        else :
            value = request.args[key]
    except:
        pass
    return value
    
@app.route('/startSSHTunnel',methods=['GET','POST'])
def doStartTunnel():        
    global gconfig
    retinf = doStart(gconfig)
    print retinf
    return retinf

@app.route('/stopSSHTunnel', methods=['GET','POST'])
def doStopTunnel():
    global gconfig
    return doStop(gconfig)

@app.route('/',methods=['GET'])
def index():
    return render_template('remote_sender.html')

if __name__ == '__main__':    
    gconfig = ConfigData('sender.xml')
    app.run(host="0.0.0.0",port=9190)
    
    
    
