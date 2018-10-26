# coding:utf8 '''
import threading
import sys,os
import logging
import json
def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance
def save_py(moudle):
    keys,py=dir(moudle),''
    for key in keys:
        if '__' in key:continue
        py+=key+'='+json.dumps(getattr(moudle,key),indent=4, separators=(',', ':'))+'\n'
    with open(moudle.__name__+".py",'w') as f:f.write(py)
@singleton
class Logger:
    def __init__(self):
        handlers = {
            logging.NOTSET: "logs/notset.logs",
            logging.DEBUG: "logs/debug.logs",
            logging.INFO: "logs/info.logs",
            logging.WARNING: "logs/warning.logs",
            logging.ERROR: "logs/error.logs",
            logging.CRITICAL: "logs/critical.logs"
        }
        self.__loggers = {}
        logLevels = handlers.keys()
        fmt = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
        for level in logLevels: #创建logger
            logger = logging.getLogger(str(level))
            logger.setLevel(level)
            #创建hander用于写日日志文件
            log_path = os.path.abspath(handlers[level])
            fh = logging.FileHandler(log_path) #定义日志的输出格式
            fh.setFormatter(fmt)
            fh.setLevel(level) #给logger添加hander
            logger.addHandler(fh)
            self.__loggers.update({level: logger})
    def info(self, message):
        self.__loggers[logging.INFO].info(message)
    def error(self, message):
        self.__loggers[logging.ERROR].error(message)
    def warning(self, message):
        self.__loggers[logging.WARNING].warning(message)
    def debug(self, message):
        self.__loggers[logging.DEBUG].debug(message)
    def critical(self, message):
        self.__loggers[logging.CRITICAL].critical(message)
class Timer():
    def __init__(self,delay,fun):
        self.delay,self.f=delay,fun
        self.t=threading.Timer(self.delay,self.fun)
        self.t.start()
    def fun(self):
        if self.f:self.f()
        self.t=threading.Timer(self.delay,self.fun)
        self.t.start()
    def cancel(self):
        self.t.cancel()
class Event():
    def __init__(self):
        self.map=[]
        self.keys=[]
    def index(self,k):
        i=-1
        for key in self.keys:
            i+=1
            if key==k:return i
        return -1
    def on(self,key,fun):
        i=self.index(key)
        if i==-1:
            self.map.append({"key":key,"funs":[fun]})
            self.keys.append(key)
        else:
            self.map[i]["funs"].append(fun)
    def emit(self,key,data=None):
        i=self.index(key)
        if i==-1:
            print("no regist event:"+str(key))
            return
        for f in self.map[i]["funs"]:f(data)
    def rm(self,key,fun):
        i=self.index(key)
        if i==-1:
            print("no regist event:"+str(key))
            return
        funs=self.map[i]["funs"]
        for j in range(len(funs)):
            if funs[j]==fun:funs[j]=None
        self.map[i]["funs"]=list(filter(None,funs))
