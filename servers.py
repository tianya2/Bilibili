from utils import Timer,Logger
from api import BilibiliAPI as API
class Login():
    def __init__(self,s):
        self.s=s
        self.oauthKey=''
        self.s._type='json'
    def isLogin(self):
        r=API.Login.isLogin(self.s)
        if r['code']==-101:return False
        else:return self.get_info()
    def get_info(self):
        r=API.User.get_info(self.s)
        self.info=r['data']
        return True
    def get_vdcode(self):
        r=API.Login.get_vdcode(self.s)
        code_url=r['data']['url']
        img=self.make_vdcode(code_url)
        self.show_img(img)
        self.oauthKey=r['data']['oauthKey']
    def show_img(self,img):
        import matplotlib.pyplot as plt
        plt.imshow(img)  
        plt.show()
    def make_vdcode(self,code_url):
        import qrcode
        return qrcode.make(code_url)
    def loop_vdcode(self):
        import time
        r=API.Login.loop_vdcode(self.s,self.oauthKey)
        while not r['status']:
            time.sleep(1)
            r=API.Login.loop_vdcode(self.s,self.oauthKey)
            if r['data']==-2:
                print('二维码已过期')
                break
        if r['status']:self.info=r['data']
        return r['status']
class Join:
    def __init__(self,Info,s):
        self.Info = Info
        self.check_roomids=[Info['roomid']]
        self.raffleId=0
        self.hour_run=Timer(7.2e3,self.each_hour_run)
        self.s=s
        self.num=1
    def join_smalltv(self,obj):
        if self.num==200:
            print('[跳过抽奖]['+obj['title']+']已跳过抽奖(roomid=' + str(obj['roomid'])+ ',raffleId=' + str(obj['raffleId'])+ ')')
            return
        self.num+=1
        res=API.Gift.join_smalltv(self.s,obj['roomid'], obj['raffleId'],self.Info['csrf_token'],self.Info['visit_id'])
        code=res['code']
        if code==0:Logger.info('[自动抽奖]['+obj['title']+']已参加抽奖(roomid=' + str(obj['roomid'])+ ',raffleId=' + str(obj['raffleId'])+ ')')
        elif code==400:Logger.warning('[自动抽奖][礼物抽奖]访问被拒绝，您的帐号可能已经被封禁，已停止')
        elif code==65531:Logger.info('[自动抽奖][礼物抽奖]已参加抽奖(roomid=' + str(obj['roomid'])+ ',raffleId=' + str(obj['raffleId'])+ ')')
        else:Logger.error('[自动抽奖][礼物抽奖]已参加抽奖(roomid=' + str(obj['roomid'])+ ',raffleId=' + str(obj['raffleId'])+ ')'+res['msg'])
    def push_and_check_roomid(self,roomid):
        self.push_roomid(roomid)
        for roomid in self.check_roomids:self.check_and_join_guard(roomid)
    def push_roomid(self,roomid):
        if roomid in self.check_roomids:return
        self.check_roomids.append(roomid)
    def each_hour_run(self):
        res=API.Room.room_rank(self.s,"master_realtime_hour",'areaid_realtime_hour')
        for room in res['data']['list']:self.push_roomid(room['roomid'])
        res=API.Room.room_rank(self.s,"week_star_master",'week')
        for room in res['data']['list']:self.push_roomid(room['roomid'])
    def check_and_join_smalltv(self,roomid):
        #res=API.Gift.check_smalltv(self.s,roomid,'v2')
        #if res['code']==-400:return
        #for data in res['data']:
        #    if data['raffleId']<=self.raffleId:continue
        #    self.raffleId=data['raffleId']
        #    self.join_smalltv({'roomid':roomid,'raffleId':self.raffleId,'title':data['title']})
        #if len(res['data'])==0:
        #    res=API.Gift.check_smalltv(self.s,roomid,'v3')
        #   for data in res['data']['list']:
        #        if data['raffleId']<=self.raffleId:continue
        #        self.raffleId=data['raffleId']
        #        self.join_smalltv({'roomid':roomid,'raffleId':self.raffleId,'title':data['title']})
        self.push_and_check_roomid(roomid)
    def join_guard(self,obj):
        res=API.Gift.join_guard(self.s,obj['roomid'],obj['id'],self.Info['csrf_token'])
        try:Logger.info(res['data']['message'])
        except Exception as e:print(e,res)
    def check_and_join_guard(self,roomid):
        res=API.Gift.check_guard(self.s,roomid)
        if len(res['data'])==0:return
        for guard in res['data']:self.join_guard({'id':guard['id'],'roomid':roomid})
        res=API.Gift.check_guard(self.s,roomid,'')
        if len(res['data']['guard'])==0:return
        for guard in res['data']['guard']:self.join_guard({'id':guard['id'],'roomid':roomid})
