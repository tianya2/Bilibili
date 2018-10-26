import threading
import json
import struct
from ws4py.client.threadedclient import WebSocketClient
from utils import Event,Timer
event=Event()
class DanmuWebSocket(WebSocketClient):
    def __init__(self,info,serveraddress='wss://broadcastlv.chat.bilibili.com/sub'):
        self.serveraddress=serveraddress
        WebSocketClient.__init__(self,serveraddress)
        DanmuWebSocket.event=event
        DanmuWebSocket.headerLength=16
        self.Info=info
    def opened(self):
        self.sendLoginPacket(self.Info['uid'],self.Info['roomid'],self.Info['protover'],self.Info['platform'],self.Info['clientver'])
        self.sendHeartBeatPacket();
        self.heartBeatHandler = Timer(20,self.sendHeartBeatPacket)
        print("opened")
    def delay_close(self):
        dws=DanmuWebSocket(self.Info,self.serveraddress)
        event.emit('reconnect',dws);
    def closed(self, code, reason=None):
        print("Closed", code, reason)
        if hasattr(self,"heartBeatHandler"):self.heartBeatHandler.cancel();
        if code == 1006: return
        threading.Timer(5,self.delay_close).start()
    def received_message(self, message):
        position,length=0,len(message.data)-1
        while position<length:
            header_pack=struct.unpack(">IHHII",message.data[position:position+16])
            length_pack=header_pack[0]
            operation=header_pack[3]
            if operation==3:
                num=header_pack[1]+position
                num=struct.unpack(">I",message.data[num:num+4])[0]
                event.emit('heartbeat',num)
            elif operation==5:
                data=json.loads(message.data[position+16:position+length_pack])
                event.emit('cmd',data)
                #print("recv:"+data["cmd"])
            else:
                event.emit('login');
            position+=length_pack
    def sendData(self,data, protover = 1, operation = 2, sequence = 1):
        if type(data)==dict:
            data=json.dumps(data).encode()
        elif type(data)==str:
            data=data.encode()
        header=struct.pack(">IHHII",DanmuWebSocket.headerLength+len(data),DanmuWebSocket.headerLength,protover,operation,sequence)
        self.send(header+data)
    def sendLoginPacket(self,uid, roomid, protover = 1, platform = 'web', clientver = '1.4.6'):
        # Uint(4byte) + 00 10 + 00 01 + 00 00 00 07 + 00 00 00 01 + Data 登录数据包
        data = {
            'uid': int(uid),
            'roomid': int(roomid),
            'protover': protover,
            'platform': platform,
            'clientver': clientver
        }
        print("sendLoginPacket")
        data=json.dumps(data)
        data=data.replace(' ','')
        self.sendData(data.encode(),1,7,1)
    def sendHeartBeatPacket(self):
        # Uint(4byte) + 00 10 + 00 01 + 00 00 00 02 + 00 00 00 01 + Data 心跳数据包
        self.sendData(b'[object Object]', 1, 2, 1);
    def bind(self,onreconnect=None,onlogin=None,onheartbeat=None,oncmd=None,onreceive =None):
        if "cmd" in event.keys:return
        if hasattr(onreconnect,"__call__"):event.on("reconnect",onreconnect)
        if hasattr(onlogin,"__call__"):event.on("login",onlogin)
        if hasattr(onheartbeat,"__call__"):event.on("heartbeat",onheartbeat)
        if hasattr(oncmd,"__call__"):event.on("cmd",oncmd)
        if hasattr(onreceive,"__call__"):event.on("receive",onreceive)
