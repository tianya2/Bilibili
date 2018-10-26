from jquery import http,session
from servers import Join,Login
from DanmuWS import DanmuWebSocket
from config import *
from utils import save_py
import config
%matplotlib inline
#save_py(config)
s=session(headers,'config/瑰叶潇潇.txt')
login=Login(s)
join=Join(post_info,s)
ws=None
while not login.isLogin():
    login.get_vdcode()
    login.loop_vdcode()
ws_info['uid']=post_info['uid']=login.info['uid']
def oncmd(data):
    cmd=data["cmd"]
    if cmd in msg_info['reject_msg']:return
    if cmd=="SYS_MSG":
        if "real_roomid" in data:join.check_and_join_smalltv(data["real_roomid"])
def onlogin(data):
    print("login success")
def onreconnect(code,data=None):
    global ws
    ws=data['dws']
room_num=0
def onheartbeat(num):
    if num>3:return
    close()
    if len(join.check_roomids)==0:
        global room_num
        join.each_hour_run()
        room_num+=1
        if room_num>3:return join.hour_run.cancel()
    ws_info['roomid']=post_info['roomid']=join.check_roomids.pop()
    main()
def main():
    global ws
    try:
        print(ws_info['roomid'])
        ws = DanmuWebSocket(ws_info,'wss://broadcastlv.chat.bilibili.com/sub')
        ws.connect()
        ws.bind(onreconnect,onlogin,onheartbeat,oncmd)
        #ws.run_forever()
    except:
        close()
def close():
    ws.close()
    save_py(config)
    s.save()
main()
