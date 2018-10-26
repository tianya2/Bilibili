import time,math
from jquery import http
from utils import singleton
def ajax(s,url,method='GET',data=None):
    if int(time.time()*1000)-BilibiliAPI.last_ajax < 10:BilibiliAPI.cnt_frequently_ajax+=1
    else:BilibiliAPI.cnt_frequently_ajax = 0
    BilibiliAPI.last_ajax = int(time.time()*1000)
    if BilibiliAPI.cnt_frequently_ajax > 20:raise RuntimeError('调用BilibiliAPI太快，可能出现了bug')
    if method=='GET':return http.get(s,url,data)
    else:return http.post(s,url,data)
class Gift():
    def check_smalltv(self,s,roomid,ver='v2'):
        url='https://api.live.bilibili.com/gift/'+ver+'/smalltv/check'
        data={'roomid': roomid}
        return ajax(s,url,'GET',data)
    def join_smalltv(self,s,roomid,raffleId,csrf_token,visit_id='', type = 'Gift'):
        url= 'https://api.live.bilibili.com/gift/v3/smalltv/join'
        data={
                'roomid': roomid,
                'raffleId': raffleId,
                'type': type,
                'csrf_token': csrf_token,
                'visit_id': visit_id
                }
        return ajax(s,url,'POST',data)
    def check_guard(self,s,roomid,_type='_guard'):
        url='https://api.live.bilibili.com/lottery/v1/Lottery/check'+_type+'?roomid='+str(roomid)
        return ajax(s,url,'GET');
    def join_guard(self,s,roomid,id,csrf_token,type='guard',visit_id=None):
        url= 'https://api.live.bilibili.com/lottery/v2/Lottery/join'
        data= {
                'roomid': roomid,
                'id': id,
                'type': type,
                'csrf_token': csrf_token,
                'visit_id': visit_id
            }
        return ajax(s,url,'POST',data)
class Room():
    def room_rank(self,s,type="week_star_master",type_id='week'):
        url='https://api.live.bilibili.com/rankdb/v1/Rank2018/getTop?type='+type+'&type_id='+type_id
        return ajax(s,url)
class Msg():
    def send(self,s,msg,roomid,csrf_token,rnd=0):
        if rnd==0:rnd=int(time.time())
        url='https://api.live.bilibili.com/msg/send'
        data={
            'color':14893055,
            'csrf_token':csrf_token,
            'fontsize':25,
            'mode':1,
            'msg':msg,
            'rnd':rnd,
            'roomid':roomid
        }
        return ajax(s,url,'POST',data)
class User():
    def get_info(self,s):
        url="https://api.live.bilibili.com/User/getUserInfo"
        return ajax(s,url)
class Login():
    def isLogin(self,s):
        url="https://account.bilibili.com/home/userInfo"
        return ajax(s,url)
    def get_vdcode(self,s):
        url="https://passport.bilibili.com/qrcode/getLoginUrl"
        return ajax(s,url)
    def loop_vdcode(self,s,oauthKey):
        url="https://passport.bilibili.com/qrcode/getLoginInfo"
        data={
                'oauthKey':oauthKey,
                'gourl': 'https://passport.bilibili.com/account/security'
            }
        return ajax(s,url,'POST',data)
@singleton
class BilibiliAPI():pass
BilibiliAPI.last_ajax=0
BilibiliAPI.cnt_frequently_ajax=0
BilibiliAPI.ajax=ajax
BilibiliAPI.Msg=Msg()
BilibiliAPI.Login=Login()
BilibiliAPI.User=User()
BilibiliAPI.Gift=Gift()
BilibiliAPI.Room=Room()
